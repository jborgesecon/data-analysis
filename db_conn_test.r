library(dplyr)
library(tidyr)
library(RSQLite)
read_sql_file <- function(file_path) {
    query <- readLines(file_path, warn=FALSE)
    return(paste(query, collapse="\n"))
}
con <- dbConnect(RSQLite::SQLite(), "economics.db")
query_file <- "queries/person.sql"
sql_query <- read_sql_file(query_file)
data <- dbGetQuery(con, sql_query)
dbDisconnect(con)
# print(data)
# print(str(data))
print(View(data))