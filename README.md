# Script Generator

A web-based tool to generate configuration scripts for MikroTik and Cisco devices.

## Features

*   Web interface for entering configuration data.
*   Generates scripts for both MikroTik and Cisco devices.
*   Automatically calculates and derives IP addresses.
*   Provides a preview of the generated script.

## Installation

1.  Clone the repository.
2.  Install Node.js dependencies:
    ```bash
    npm install
    ```
3.  This project uses Python for script generation, but it relies on standard libraries, so no additional Python dependencies are required.

## Usage

1.  Start the server:
    ```bash
    npm start
    ```
2.  Open your browser and go to `http://localhost:3104`.

## API Endpoints

*   `POST /run/mkt`: Generates a MikroTik script.
*   `POST /run/cisco`: Generates a Cisco script.

## Technologies Used

*   Node.js
*   Express
*   Python
