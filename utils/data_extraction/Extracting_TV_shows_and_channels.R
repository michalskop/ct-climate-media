#Code to collect the tv channels and then show's names and id, to easier get access to which id belongs to which show.
library(dplyr)
# Get the names of all .rds files in the folder
files <- list.files(path = "~/Rprojekt/Climate/1.data_extraction/data/full_articles", pattern = "*.rds", full.names = TRUE)

# Define a function to read each file and extract the SourceName and Code columns
extract_columns <- function(file) {
  data <- readRDS(file)
  data[c("SourceName", "Code")]
}

# Apply the function to each file
TvChannels <- lapply(files, extract_columns)

# Combine the data frames into one
TvChannels <- do.call(rbind, TvChannels)

#To get channels

TVshowChannels <- Tvshows %>%
  distinct(SourceName)

write_csv2(TVshowChannels, file = "TvShowChannels.csv", quote = "none")

#Now for the show names
# Get the names of all .rds files in the folder
channel_files <- list.files(path = "~/Rprojekt/Climate/1.data_extraction/data/annotated_articles", pattern = "*.rds", full.names = TRUE)

# Define a function to read each file and extract the SourceName and Code columns
extract_columns <- function(file) {
  data <- readRDS(file)
  data[c("section", "code")]
}

# Apply the function to each file
Tvshows <- lapply(channel_files, extract_columns)

# Combine the data frames into one, with id and name
Tvshows <- do.call(rbind, Tvshows)
Tvshows <- as.data.frame(Tvshows)

#To get shows

TVshowsName <- Tvshows %>%
  distinct(section)

write_csv2(TVshowsName, file = "TvShowNames.csv", quote = "none")
