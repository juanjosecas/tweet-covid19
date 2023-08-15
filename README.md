# COVID-19 Data Analysis Script

This script is designed to download, analyze, and visualize COVID-19 data using Python. It fetches COVID-19 data from the "Our World in Data" dataset and provides insights into daily cases, deaths, vaccinations, and testing.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/your-username/covid-data-analysis.git
   cd covid-data-analysis
   ```

2. Install the required Python packages using pip:

   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:

   ```sh
   python analyze_covid_data.py
   ```

   This will download the COVID-19 dataset, analyze the data, create visualizations, and save the results as images.

2. Check the generated images in the current directory, showcasing different aspects of COVID-19 data.

## Features

- Downloads COVID-19 data from "https://covid.ourworldindata.org/data/owid-covid-data.csv".
- Analyzes daily cases, deaths, vaccinations, and testing data.
- Creates visualizations of key metrics using Matplotlib.
- Generates plots of daily cases, deaths, vaccinations, and testing with smoothed averages.
- Detects and highlights peaks in cases and deaths.
- Shares the results on Twitter using the Tweepy library.

## Dependencies

- Pandas
- NumPy
- Matplotlib
- SciPy
- pycountry
- requests
- tqdm
- tweepy

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or a pull request in this repository.

## License

This project is licensed under the [MIT License](LICENSE).
