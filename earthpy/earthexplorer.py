import json
import os
import tarfile
import time
import zipfile
from getpass import getpass

import requests

from .io import HOME, DATA_NAME

class BBox:
    def __init__(self, llx, lly, urx, ury):
        self.llx, self.lly, self.urx, self.ury = llx, lly, urx, ury

    @property
    def spatial_filter(self):
        return {
            'filterType': "mbr",
            'lowerLeft': {'latitude': self.lly, 'longitude': self.llx},
            'upperRight': {'latitude': self.ury, 'longitude': self.urx}}

class EarthExplorerDownloader:

    base_url = "https://m2m.cr.usgs.gov/api/api/json/stable/{endpoint}"
    dld_file_tmpl = '{display_id}.{ext}'

    def __init__(self, dataset, label, bbox, start, end,
                 file_type='zip', store_credential=False):
        self.api_key = None
        self.ext = file_type
        self.store_credential = store_credential
        self.login()
        
        self.dataset, self.label = dataset, label
        self.bbox, self.start, self.end = bbox, start, end
        
        self.temporal_filter = {'start': start, 'end': end}
        self.acquisition_filter = self.temporal_filter
        
        self.data_dir = os.path.join(HOME, DATA_NAME, self.label)
        self.path_tmpl = os.path.join(self.data_dir, self.dld_file_tmpl)
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        self._dataset_alias = None

    def get_ee_login_info(self, info_type):
        # Collect and store login info
        info_path = os.path.join(HOME, '.ee_{}'.format(info_type))
        info = None
        if os.path.exists(info_path) and self.store_credential:
            with open(info_path, 'r') as info_file:
                return info_file.read()
        if info_type=='username':
            info = input('Enter EarthExplorer {}: '.format(info_type))
        if info_type=='password':
            info = getpass('Enter EarthExplorer {}: '.format(info_type))
        if self.store_credential:
            with open(info_path, 'w') as info_file:
                info_file.write(info)
        return info

    def login(self):
        if self.api_key is None:
            login_payload = {
                'username': self.get_ee_login_info('username'), 
                'password': self.get_ee_login_info('password')}
            self.api_key = self.post("login", login_payload)
            print('Login Successful.')
        
    @property
    def headers(self):
        if self.api_key is None:
            return None
        return  {'X-Auth-Token': self.api_key}
    
    def logout(self):
        self.post("logout", None)
        print("Logged Out\n\n")

    def post(self, endpoint, data):
        # Send POST requests
        url = self.base_url.format(endpoint=endpoint)
        response = requests.post(url, json.dumps(data), headers=self.headers)
        
        # Raise any HTTP Errors
        response.raise_for_status()
        
        # Return data
        return response.json()['data']
    
    @property
    def dataset_alias(self):
        if self._dataset_alias is None:
            print("Searching datasets...")
            params = {
                'datasetName': self.dataset,
                'spatialFilter': self.bbox.spatial_filter,
                'temporalFilter': self.temporal_filter}
            datasets = self.post("dataset-search", params)
            
            # Get a single dataset alias
            if len(datasets) > 1:
                print(datasets)
                raise ValueError('Multiple datasets found - refine search.')
            self._dataset_alias = datasets[0]['datasetAlias']
            
            print('Using dataset alias: {}'.format(self._dataset_alias))
        return self._dataset_alias
    
    def find_scene_ids(self):
        params = {
            'datasetName': self.dataset_alias,
            'startingNumber': 1,
            
            'sceneFilter': {
                'spatialFilter': self.bbox.spatial_filter,
                'acquisitionFilter': self.acquisition_filter}}
        
        print("Searching scenes...")
        scenes = self.post("scene-search", params)
        print('Found {} scenes'.format(scenes['recordsReturned']))
        return scenes
    
    def find_available_product_info(self):
        scenes = self.find_scene_ids()
        params = {
            'datasetName': self.dataset_alias, 
            'entityIds': [scene['entityId'] for scene in scenes['results']]}
        products = self.post("download-options", params)

        # Aggregate a list of available products
        product_info = []
        for product in products:
            # Make sure the product is available for this scene
            if 'proxied' in product:
                proxied = product['proxied']
            else:
                proxied = False
            if product['available']==True or proxied==True:
                product_info.append({
                    'entityId': product['entityId'],
                    'productId': product['id']})
        if not product_info:
            raise ValueError('No available products.')
        print('{} products found.'.format(len(product_info)))
        return product_info

    def submit_download_request(self):
        product_info = self.find_available_product_info()
        # Did we find products?
        if product_info:
            # Request downloads
            params = {
                'downloads': product_info,
                'label': self.label}
            downloads = self.post("download-request", params)
            print('Downloads staging...')
        else:
            raise ValueError(
                'No products found with the specified boundaries.')
    
    def check_download_status(self):
        params = {'label': self.label}
        downloads = self.post("download-retrieve", params)
        return downloads
    
    def wait_for_available_downloads(self, timeout=None):
        keep_waiting = True
        while keep_waiting:
            downloads = self.check_download_status()
            n_queued = downloads['queueSize']
            keep_waiting = n_queued > 0
            if keep_waiting:
                print("\n", n_queued,
                      "downloads queued but not yet available. "
                      "Waiting for 30 seconds.\n")
                time.sleep(30)
            
            if not timeout is None:
                timeout -= 30
                if timeout < 0:
                    break
        
        return downloads
        
    def download(self, wait=True, timeout=None, override=True):
        # Check download status
        if wait:
            downloads = self.wait_for_available_downloads(timeout=timeout)
        else:
            downloads = self.check_download_status()
            
        available_or_proxied = (
            downloads['available'] 
            + [dld for dld 
               in downloads['requested'] if dld['statusCode']=='P'])
        if len(available_or_proxied)==0:
            raise ValueError('No available downloads.')
        
        # Download available downloads
        for download in available_or_proxied:
            # Download and save compressed file
            dld_path = self.path_tmpl.format(
                display_id=download['displayId'], ext=self.ext)
            print(dld_path)
            # Cache downloads
            if override or (not os.path.exists(dld_path)):
                print('Saving download: {}'.format(download['displayId']))
                with open(dld_path, 'wb') as dld_file:
                    response = requests.get(download['url'])
                    dld_file.write(response.content)
            
            # Remove download from M2M system
            params = {'downloadId': download['downloadId']}
            self.post('download-remove', params)
            
            self.uncompress(dld_path)
                    
    def uncompress(self, download_path):
        # Extract compressed files
        if self.ext=='tar':
            with tarfile.TarFile(download_path, 'r') as dld_tarfile:
                dld_tarfile.extractall(self.data_dir)
        if self.ext=='zip':
            with zipfile.ZipFile(download_path, 'r') as dld_zipfile:
                dld_zipfile.extractall(self.data_dir)