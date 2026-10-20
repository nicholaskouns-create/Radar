"""Source registry. URLs are data sources, not executable dependencies."""
SOURCES = {
 "acicula-iq-v3": {
   "url": "https://huggingface.co/datasets/ACICULA/mocap2radar/resolve/main/raw/v3/radar/DiagonalLong2Fast.csv",
   "sha256": "197905b5ec4c4b8eaeb291ead3e9847a9696be2b6f5726047c7e18789dbcb00d",
   "status": "real_iq_descriptive",
   "labels_verified": False,
   "adc_cube_verified": False,
 },
 "radr-metadata": {
   "url": "https://huggingface.co/datasets/radr-anon-2026/radr/resolve/main/synced_hdf5/degrade0.h5",
   "sha256": "f4db4bbd4f5c7796093783a777428eb34504ccd2bc8dae51453f64ddd50af525",
   "status": "metadata_only",
   "labels_verified": False,
   "adc_cube_verified": False,
 },
}
