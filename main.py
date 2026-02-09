# this file runs the main function to create the app
# 2022 revised 2026

# imports
from website import create_app

#app = create_app()
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)