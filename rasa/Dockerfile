FROM rasa/rasa:3.6.20

# Set working directory
WORKDIR /app

# Install rasa-sdk for custom actions
USER root
RUN pip install rasa-sdk==3.6.2
USER 1001

# Copy configuration files
COPY . /app

# Expose ports
EXPOSE 5005 5055

# Run Rasa server
CMD ["run", "--enable-api", "--cors", "*", "--debug"]
