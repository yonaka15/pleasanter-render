# Pleasanter with Extended SQLs
FROM implem/pleasanter:1.4.17.0

# Copy extended SQLs to the appropriate directory
# Note: /app is the content root path for Pleasanter
COPY extended_sqls/ /app/App_Data/Parameters/ExtendedSqls/

# Ensure proper permissions
RUN chmod -R 644 /app/App_Data/Parameters/ExtendedSqls/ || true

# Add metadata
LABEL description="Pleasanter with pre-configured Extended SQLs"
LABEL version="1.0.0"
LABEL maintainer="pleasanter-render-project"
