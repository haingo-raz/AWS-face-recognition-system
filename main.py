from website import create_app

#Create and run application
app = create_app()

#run the web server directly with this file
if __name__ == '__main__':
    app.run(host="localhost", port=5000, debug=True)