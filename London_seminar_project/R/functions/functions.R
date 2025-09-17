# Our package function
package_check <- function(need = c(), groundhog.date = "2025-01-01"){
  require(groundhog, quietly = TRUE)
  have <- need %in% rownames(installed.packages()) # checks packages you have
  if(any(!have)) install.packages(need[!have]) # install missing packages
  invisible(lapply(need, groundhog::groundhog.library, date = groundhog.date))
}

# We build a re-usable function to download data from a particular site, and store it on our local drive: 
file_grabber <- function(file_name_dl, file_path, file_name_final = NULL, url, compressed = TRUE) {
  # Check if the file has already been downloaded -- do not re-download if so
  if (!file.exists(paste0(file_path, file_name_dl))) {
    download.file(url, paste0(file_path, file_name_dl), mode = "wb")
    print("File downloaded.")
  } else {
    print("File already downloaded.")
  }
  
  # If file is compressed and not already unzipped, perform unzipping, otherwise do nothing
  if (compressed && !file.exists(paste0(file_path, '/shapefiles/', file_name_final))) {
    unzip(paste0(file_path, file_name_dl), exdir = paste0(file_path, "shapefiles"))
    print("File unzipped.")
  } else {
    print("File already unzipped or no need for unzipping.")
  }
}
