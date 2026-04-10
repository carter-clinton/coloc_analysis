# src/R/utils/load_config.R
# Loads config/pipeline.yaml and provides path resolution for R scripts
# called from Snakemake rules.
#
# Usage from Snakemake shell directive:
#   Rscript scripts/my_analysis.R --config-path {config_path}
#
# Usage in R script:
#   source("src/R/utils/load_config.R")
#   cfg <- load_pipeline_config()
#   sumstats_dir <- resolve_path(cfg, "paths", "harmonized_sumstats")

#' Load the pipeline configuration from config/pipeline.yaml
#'
#' @param config_path Path to pipeline.yaml. If NULL, parsed from
#'   --config-path CLI arg or defaults to "config/pipeline.yaml".
#' @return Named list of configuration values.
load_pipeline_config <- function(config_path = NULL) {
  if (is.null(config_path)) {
    args <- commandArgs(trailingOnly = TRUE)
    idx <- which(args == "--config-path")
    if (length(idx) > 0 && idx < length(args)) {
      config_path <- args[idx + 1]
    } else {
      config_path <- "config/pipeline.yaml"
    }
  }

  if (!file.exists(config_path)) {
    stop(paste("Config file not found:", config_path))
  }

  if (!requireNamespace("yaml", quietly = TRUE)) {
    stop("Package 'yaml' is required. Install with: install.packages('yaml')")
  }

  cfg <- yaml::read_yaml(config_path)
  cfg
}

#' Resolve a nested config key to its value
#'
#' @param cfg Config list from load_pipeline_config().
#' @param ... Key path components (e.g., "paths", "harmonized_sumstats").
#' @return The resolved value from the config.
resolve_path <- function(cfg, ...) {
  keys <- list(...)
  val <- cfg
  for (k in keys) {
    if (is.null(val[[k]])) {
      stop(paste("Config key not found:", paste(keys, collapse = " -> ")))
    }
    val <- val[[k]]
  }
  val
}

#' Get all traits from config
#'
#' @param cfg Config list from load_pipeline_config().
#' @return Character vector of trait names.
get_traits <- function(cfg) {
  if (is.null(cfg[["traits"]])) {
    stop("Config missing 'traits' key")
  }
  unlist(cfg[["traits"]])
}

#' Get all ancestries from config
#'
#' @param cfg Config list from load_pipeline_config().
#' @return Character vector of ancestry codes.
get_ancestries <- function(cfg) {
  if (is.null(cfg[["ancestries"]])) {
    stop("Config missing 'ancestries' key")
  }
  unlist(cfg[["ancestries"]])
}

#' Get ancestries available for a specific trait
#'
#' @param cfg Config list from load_pipeline_config().
#' @param trait Trait name (e.g., "bmi").
#' @return Character vector of ancestry codes for this trait.
get_trait_ancestries <- function(cfg, trait) {
  ta <- cfg[["trait_ancestries"]]
  if (is.null(ta) || is.null(ta[[trait]])) {
    stop(paste("No trait_ancestries entry for trait:", trait))
  }
  unlist(ta[[trait]])
}
