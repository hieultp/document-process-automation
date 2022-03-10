from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files("skimage")

hiddenimports = ["skimage.io", "skimage.transform", "skimage.filters.edges"]
