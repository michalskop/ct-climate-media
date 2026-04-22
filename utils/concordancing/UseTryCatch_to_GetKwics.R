get_kwics <- function(udpipe_chunk) {

  # Use tryCatch to catch any errors that occur during the execution of the function
  tryCatch({

    # We use DTPLYR for faster workflow.
    corpus_chunk <- udpipe_chunk %>%
      readRDS() %>%
      lazy_dt() %>%
      filter(upos %in% upos_filter) %>%
      mutate(doc_id,
             sentence_id,
             # Select token or lemma for different results
             word = str_replace_na(!!sym(lemma_or_token), replacement = ""),
             .keep = "none") %>%
      {if(lowercase) mutate(., word = tolower(word)) else .} %>%
      # Aggregate lemma to the level of individual texts.
      group_by(doc_id) %>%
      summarize(tokenized_text = str_squish(str_c(word, collapse = " "))) %>%
      ungroup() %>%
      as_tibble() %>%
      corpus(docid_field = "doc_id", text_field = "tokenized_text") %>%
      tokens()

    concordance_key_words <- function(term_of_interest, corpus_chunk) {
      kwic(
        x = corpus_chunk,
        window = max_words_context,
        pattern = term_of_interest["key_word"],
        valuetype = "regex",
        case_insensitive = !lowercase
      )  %>%
        as_tibble()  %>%
        {if(!is.na(term_of_interest[["filter_main"]])) filter(., str_detect(.$keyword, regex(term_of_interest[["filter_main"]], ignore_case = !lowercase), negate = TRUE)) else .} %>%
        {if(!is.na(term_of_interest[["filter_pre"]])) filter(., str_detect(.$pre, regex(term_of_interest[["filter_pre"]], ignore_case = !lowercase), negate = TRUE)) else .} %>%
        {if(!is.na(term_of_interest[["filter_post"]])) filter(., str_detect(.$post, regex(term_of_interest[["filter_post"]], ignore_case = !lowercase), negate = TRUE)) else .}
    }

    kwic_chunk_combined <- lapply(kwic_pattern_regex, concordance_key_words, corpus_chunk) %>% bind_rows()

    print(paste("Chunk", udpipe_chunk, "finished concordancing."))

    return(kwic_chunk_combined)

  }, error = function(e) {
    # Print an error message if an error occurs
    print(paste("Error in chunk", udpipe_chunk, ":", conditionMessage(e)))
    return(NULL)
  })
}
