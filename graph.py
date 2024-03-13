from matplotlib import pyplot
import datetime
import requests
import numpy as np


class Make_Graph:
    """A class to get data and create graphs."""
    def __init__(self, from_curr, to_curr, from_date, to_date, source):
        """Initialize class"""
        self.from_curr = from_curr
        self.to_curr = to_curr
        self.from_date = from_date
        self.to_date = to_date
        self.source_list = source

    def get_data_for_graph(self):
        """Get data needed to make graph"""
        date_list = list()  # list of dates in the graph
        rate_list = list()  # list of rates in the graph
        # calculate data length
        from_date_value = datetime.date(int(self.from_date[0:4]), int(self.from_date[5:7]), int(self.from_date[8:10]))
        to_date_value = datetime.date(int(self.to_date[0:4]), int(self.to_date[5:7]), int(self.to_date[8:10]))
        delta = to_date_value - from_date_value
        # loop to add data to graph
        for date in range(0, delta.days + 1, 1):
            date_list.append(self.source_list[date][0])
            rate_list.append(float(self.source_list[date][1]))
        # return date list, rate list and len of data
        return date_list, rate_list, delta.days

    def y_range(self):
        """Function to determine the range for y-axis based on actual data."""
        # determine range for y axis
        values = []
        delta = self.get_data_for_graph()[2]
        for date in range(0, delta, 1):
            values.append(self.source_list[date][1])
        lower_range = 0.7 * min(values)
        upper_range = 1.3 * max(values)
        return lower_range, upper_range

    def make_graph(self):
        """Function to generate graph"""
        # get data needed
        date_list = self.get_data_for_graph()[0]
        rate_list = self.get_data_for_graph()[1]

        # formatting x-axis via subplot to avoid overlapping
        fig, ax = pyplot.subplots(1, figsize=(16, 6))
        ax.grid()
        fig.autofmt_xdate()
        p = len(date_list)
        if 30 < p < 60:
            ax.set_xticks(np.arange(0, p, 5))
        if p > 60:
            ax.set_xticks(np.arange(0, p, 10))

        # generate graph
        pyplot.plot(date_list, rate_list,'ro--', linewidth=2, label=f'{self.from_curr} over {self.to_curr} '
                                                                   f'from {self.from_date} to {self.to_date}')
        # formatting y-axis range
        pyplot.ylim((self.y_range()[0], self.y_range()[1]))
        # labels, legends and show graph
        pyplot.xlabel("Date")
        pyplot.ylabel("FX Rates")
        pyplot.legend(loc="upper left")
        fig.show()


def getDataFromAPI(from_curr, to_curr, from_date, to_date):
    """Function to get data from microservice"""
    url = 'http://localhost:5000/price-history'
    params = {
        'currency_1': from_curr,
        'currency_2': to_curr,
        'start_date': from_date,
        'end_date': to_date
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['price_history']
    else:
        print('Request failed with status code:', response.status_code)
        return response
