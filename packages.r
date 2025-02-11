# # Installing a new package:

packs <- c(
    "languageserver",
    "installr",
    "ggplot2",
    "dplyr",
    "tidyr",
    "tidyverse",
    "caTools",
    "caret",
    "e1071",
    "naivebayes",
    "randomForest",
    "kernlab",
    "DBI",
    "RPostgreSQL",
    "fakir",
    "plm",
    "RSQLite"
)

install.packages(packs, dependencies = TRUE)

# install.packages("rmarkdown")           # Used for '.rmd' tasks
# install.packages("tinytex")             # Used for '.rmd' tasks
#     library(tinytex)
#     tinytex::install_tinytex()