# Create an empty list to store the doc_id
doc_id_list <- list()

library(purrr)
library(dplyr)

# Get the list of .rds files
files <- list.files("~/Rprojekt/Climate/2.data_transformations/data/udpipe_processed/", pattern = "\\.rds$", full.names = TRUE)

# Read each .rds file, extract the doc_id column, and combine them into a data frame
doc_id_df <- map_dfr(files, ~readRDS(.x) %>% select(doc_id))

# Get the unique values of the doc_id variable HERE IT STARTS GOING WRONG
unique_doc_ids <- doc_id_df(df$doc_id)

# Convert the unique_doc_ids character vector into a data frame
unique_doc_ids_df <- data.frame(doc_id = unique_doc_ids)

# Count the number of occurrences of each unique doc_id
doc_id_counts <- table(unique_doc_ids_df$doc_id)

# Convert the table to a data frame for easier manipulation
doc_id_counts_df <- as.data.frame.table(doc_id_counts)

# Rename the columns for clarity
names(doc_id_counts_df) <- c("doc_id", "count")

# Count the number of unique doc_id values
num_unique_doc_ids <- length(unique_doc_ids)

num_unique_doc_ids

# Get the unique values of the article_id variable
unique_article_ids <- unique(climate_corpus_v4$article_id)

# Count the number of unique article_id values
num_unique_article_ids <- length(unique_article_ids)

num_unique_article_ids

# New try -----------------------------------------------------------------
library(purrr)
library(dplyr)

# Get the list of .rds files
files <- list.files("~/Rprojekt/Climate/2.data_transformations/data/udpipe_processed/", pattern = "\\.rds$", full.names = TRUE)

# Read each .rds file, extract the doc_id column, and combine them into a data frame
doc_id_df <- map_dfr(files, ~readRDS(.x) %>% select(doc_id))

