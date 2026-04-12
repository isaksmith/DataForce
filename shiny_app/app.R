library(shiny)
library(readr)
library(dplyr)
library(ggplot2)
library(DT)
library(plotly)
library(tidyr)

base_path <- file.path("..", "Hack The Plains 2026 Datasets")

datasets <- list(
  "Branches" = "branches.csv",
  "Customers" = "customers.csv",
  "Digital Sessions" = "digital_sessions.csv",
  "Error Codes" = "error_codes.csv",
  "Feature Costs" = "feature_costs.csv",
  "Support Interactions" = "support_interactions.csv"
)

load_dataset <- function(label) {
  read_csv(file.path(base_path, datasets[[label]]), show_col_types = FALSE)
}

ui <- fluidPage(
  titlePanel("DataForce Shiny Explorer"),
  sidebarLayout(
    sidebarPanel(
      selectInput("dataset", "Dataset", choices = names(datasets)),
      uiOutput("dynamic_filters")
    ),
    mainPanel(
      fluidRow(
        column(4, wellPanel(h4("Rows"), textOutput("rows"))),
        column(4, wellPanel(h4("Columns"), textOutput("cols")))
      ),
      plotlyOutput("plot", height = "420px"),
      DTOutput("table")
    )
  )
)

server <- function(input, output, session) {
  dataset_reactive <- reactive({
    load_dataset(input$dataset)
  })

  output$dynamic_filters <- renderUI({
    df <- dataset_reactive()
    choices <- names(df)
    if (length(choices) == 0) return(NULL)
    selectInput("filter_col", "Optional filter column", choices = c("None", choices))
  })

  filtered_data <- reactive({
    df <- dataset_reactive()
    if (is.null(input$filter_col) || input$filter_col == "None") {
      return(df)
    }
    df
  })

  output$rows <- renderText(nrow(filtered_data()))
  output$cols <- renderText(ncol(filtered_data()))

  output$table <- renderDT({
    datatable(head(filtered_data(), 500), options = list(scrollX = TRUE, pageLength = 10))
  })

  output$plot <- renderPlotly({
    df <- filtered_data()
    label <- input$dataset

    if (label == "Branches") {
      p <- df %>% count(branch_state) %>% ggplot(aes(branch_state, n, fill = branch_state)) + geom_col() + labs(x = "State", y = "Count")
    } else if (label == "Customers") {
      p <- df %>% count(segment) %>% ggplot(aes(reorder(segment, n), n, fill = segment)) + geom_col() + coord_flip() + labs(x = "Segment", y = "Count")
    } else if (label == "Digital Sessions") {
      p <- df %>% count(session_outcome) %>% ggplot(aes(session_outcome, n, fill = session_outcome)) + geom_col() + labs(x = "Outcome", y = "Count")
    } else if (label == "Error Codes") {
      sessions_df <- load_dataset("Digital Sessions") %>%
        mutate(error_code = ifelse(is.na(error_code), "NA", as.character(error_code)),
               feature_used = ifelse(is.na(feature_used), "Unknown", as.character(feature_used)))

      error_summary <- sessions_df %>%
        count(error_code, feature_used, name = "feature_count") %>%
        arrange(error_code, desc(feature_count)) %>%
        group_by(error_code) %>%
        slice(1) %>%
        ungroup() %>%
        rename(top_feature = feature_used) %>%
        left_join(sessions_df %>% count(error_code, name = "session_count"), by = "error_code") %>%
        inner_join(df, by = "error_code") %>%
        arrange(desc(session_count)) %>%
        slice_head(n = 10)

      p <- error_summary %>%
        ggplot(aes(x = session_count, y = reorder(error_code, session_count), size = session_count, color = top_feature,
                   text = paste0("Error: ", error_code,
                                 "<br>Description: ", description,
                                 "<br>Sessions: ", session_count,
                                 "<br>Top feature: ", top_feature))) +
        geom_point(alpha = 0.8) +
        labs(x = "Linked sessions", y = "Error code", color = "Top feature", size = "Session volume")
    } else if (label == "Feature Costs") {
      tidy <- tidyr::pivot_longer(df, cols = c(avg_cost_per_success_usd, avg_cost_per_failure_usd), names_to = "cost_type", values_to = "usd_cost")
      p <- tidy %>% ggplot(aes(feature_canonical, usd_cost, fill = cost_type)) + geom_col(position = "dodge") + labs(x = "Feature", y = "USD cost")
    } else {
      p <- df %>% count(interaction_type) %>% ggplot(aes(interaction_type, n, fill = interaction_type)) + geom_col() + labs(x = "Interaction type", y = "Count")
    }

    ggplotly(p)
  })
}

shinyApp(ui, server)
