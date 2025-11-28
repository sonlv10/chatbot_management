FROM rasa/rasa:3.6.20

# Set working directory
WORKDIR /app

# Copy configuration files
COPY . /app

# Expose port
EXPOSE 5005

# Run Rasa server
CMD ["run", "--enable-api", "--cors", "*", "--debug"]
