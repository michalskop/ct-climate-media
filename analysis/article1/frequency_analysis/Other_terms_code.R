# Load necessary libraries
library(dplyr)
library(purrr)
library(lubridate)
library(ggplot2)
library(parallel)
library(readr)

# Define terms of interest
other_terms <- c("banka", "dálnice", "fotbal", "kovid", "covid", "útok")

# Get list of .rds files
list_of_processed_chunks <- list.files(path = "~/Rprojekt/Climate/2.data_transformations/data/udpipe_processed", pattern = "*.rds", full.names = TRUE)

# Define function to process each file
get_other_term_counts <- function(chunk_path) {
  data <- readRDS(chunk_path) %>%
    filter(upos == "NOUN") %>%
    transmute(doc_id, lemma = tolower(lemma)) %>%
    inner_join(doc_id_by_date, by = "doc_id") %>%
    mutate(date = as.Date(date))

  return(data)
}

# Apply function to each file
other_term_counts_list <- if (Sys.info()[['sysname']] == "Windows") {
  lapply(list_of_processed_chunks, get_other_term_counts)
} else {
  mclapply(list_of_processed_chunks, get_other_term_counts, mc.cores = detectCores() - 2)
}

# Bind results together into one data frame
other_term_counts_df <- bind_rows(other_term_counts_list)

# Convert date to monthly format
other_term_counts_df <- other_term_counts_df %>%
  mutate(month = floor_date(date, "month"))

other_term_counts_df <- other_term_counts_df %>% filter(lemma %in% other_terms)
write_csv(other_term_counts_df, file = "other_terms.csv", quote = "none")

# Summarize data to monthly counts
monthly_counts <- other_term_counts_df %>%
  group_by(month, lemma) %>%
  summarise(count = n(), .groups = "drop")

# Plot data
ggplot(monthly_counts, aes(x = month, y = count, color = lemma)) +
  geom_line() +
  scale_x_date(date_breaks = "3 month", date_labels = "%Y-%m") +
  theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) +
  labs(x = "Month", y = "Count", color = "Term")
ggsave("other_term_counts_plot.png", width = 15, height = 10, dpi = 600)
