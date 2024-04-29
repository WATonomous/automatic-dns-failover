# Use the official Nginx image as a parent image
FROM nginx:latest

# Copy the custom Nginx config file into the container
COPY default.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx when the container has provisioned
CMD ["nginx", "-g", "daemon off;"]
