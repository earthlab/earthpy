import os
import pytest
from shapely.geometry import Polygon
import earthpy.spatial as es


@pytest.fixture
def output_dir(out_path):
    return out_path[:-8]


def test_crop_all_returns_list(in_paths, output_dir, basic_geometry_gdf):
    """Test that crop all returns a list."""
    img_list = es.crop_all(
        in_paths, output_dir, basic_geometry_gdf, overwrite=True
    )
    assert type(img_list) == list


def test_crop_all_files_exist(in_paths, output_dir, basic_geometry_gdf):
    """Test that crop all actually creates the files in the directory."""
    img_list = es.crop_all(
        in_paths, output_dir, basic_geometry_gdf, overwrite=True
    )
    for files in img_list:
        assert os.path.exists(files)


def test_crop_all_fails_overwrite(in_paths, output_dir, basic_geometry_gdf):
    """Test that crop all fails when overwrite isn't set to True if files
    already exist."""
    with pytest.raises(ValueError, match="The file "):
        es.crop_all(in_paths, output_dir, basic_geometry_gdf)


def test_crop_all_fails_bad_dir(in_paths, basic_geometry_gdf):
    """Test crop all fails if user provides a bad directory path."""
    bad_path = "Bad/Path"
    with pytest.raises(ValueError, match="The output directo"):
        es.crop_all(in_paths, bad_path, basic_geometry_gdf, overwrite=True)


def test_crop_all_returns_list_of_same_len(
    in_paths, output_dir, basic_geometry_gdf
):
    """Test that crop all returns a list of the same length as the input
    list."""
    img_list = es.crop_all(
        in_paths, output_dir, basic_geometry_gdf, overwrite=True
    )
    assert len(img_list) == len(in_paths)


def test_crop_all_verbose(in_paths, output_dir, basic_geometry_gdf):
    """Test that when verbose is set to false, nothing is returned."""
    out_list = es.crop_all(
        in_paths, output_dir, basic_geometry_gdf, overwrite=True, verbose=False
    )
    assert out_list is None


def test_crop_all_with_geoms(in_paths, output_dir, basic_geometry):
    """Test crop all works with geoms instead of a gdf."""
    test = es.crop_all(in_paths, output_dir, [basic_geometry], overwrite=True)
    assert isinstance(test, list)


def test_crop_all_with_non_overlapping_geom(in_paths, output_dir):
    """Test crop all if extents don't overlap."""
    bad_geom = Polygon(
        [(12, 12), (12, 14.25), (14.25, 14.25), (14.25, 12), (12, 12)]
    )
    with pytest.raises(ValueError, match="Input shapes do not ov"):
        es.crop_all(in_paths, output_dir, [bad_geom], overwrite=True)
