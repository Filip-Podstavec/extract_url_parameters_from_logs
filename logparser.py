# Import libraries
import argparse
import sys
import re
import pandas as pd
import urllib.parse as urlparse
from collections import OrderedDict


BOTS = OrderedDict([
    ('Googlebot regular', r'Googlebot\/'),
    ('All Googlebot requests (including images,...)', r'Googlebot'),
    ('Googlebot-Images', r'Googlebot-Images'),
    ('Googlebot-News', r'Googlebot-News'),
    ('Bingbot', r'bingbot\/'),
    ('Yahoo', r'Slurp'),
    ('Yandex', r'YandexBot'),
    ('Baidu', r'Baiduspider'),
])


def main():
    args = parse_arguments()

    # Let user pick bot user-agent
    bot_user_agent = let_user_pick()
    print('\nBot user-agent picked. Analyzing log file with bot regex pattern: ' + bot_user_agent + '\n')

    # Analyze access-log line by line and store only URLs with GET parameters crawled by specific bot
    urls = extract_matching_urls(args.access_log, bot_user_agent)

    # Analyze and aggregate URLs by their parameters
    parameters = aggregate_parameters(urls)

    # Export detailed info about parameters to CSV
    parameters.to_csv(args.output, index=False)

    # Show first ten most frequent parameters in console
    print(parameters.to_string(
        index=False,
        columns=['parameter', 'request_count', 'example_url'],
        header=['Parameter', 'Request Count', 'Sample URL'],
        max_rows=10,
    ))


def parse_arguments():
    """
    Parses command-line arguments.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('access_log', help='Path to the access log file.')
    parser.add_argument('--output', metavar='FILE', default='parameters.csv', help='Path to the output file.')
    return parser.parse_args()


def let_user_pick():
    """
    Let user to choose from the list of prepared bot user-agents

    :return: Selected user agent.
    """

    # Define bot user agents to recognize in access log
    bot_user_agents = list(BOTS.values())
    bot_names = list(BOTS.keys())

    print('Please select which bot do you want to analyze:')
    for idx, element in enumerate(bot_names):
        print("{}) {}".format(idx + 1, element))
    i = input("Enter number: ")
    try:
        if 0 < int(i) <= len(bot_names):
            return bot_user_agents[int(i) - 1]
    except ValueError:
        # Skip invalid integers.
        pass

    print('Please select one of the numbers above!')
    sys.exit(1)


def extract_matching_urls(file, bot):
    """
    Analyze access-log line by line, extract URLs with GET parameters and return them in array

    :param file: path to access log
    :param bot: regex to extract specific bot
    :return: array of URLs with GET parameter crawled by specific bot
    """

    i = 0

    urls = []
    print('Processing access log:')
    with open(file) as f:
        for row in f:
            # Find only URLs with GET parameters crawled by specific bot and store them in urls array
            result = re.findall(r".*GET\s(.*\?.*)\sHTTP.*{0}.*".format(bot), row)
            if i % 100000 == 0:
                print(str(i) + ' rows processed')
            i = i + 1
            if result:
                urls.append(result[0])
    return urls


def aggregate_parameters(urls):
    """
    Aggregate extracted URL, analyze their GET parameters and return detailed analysis for each parameter

    :param urls: array of extracted URLs with GET parameters
    :return: dataframe with parameters and detailes about them
    """

    parameters = []

    for url in urls:
        parsed = urlparse.urlparse(url)
        parsed = urlparse.parse_qs(parsed.query)
        for parameter, value in parsed.items():
            parameters.append(
                {
                    'request_count': 1,
                    'parameter': parameter,
                    'parameter_value_length': len(str(value)),
                    'url_average_length': len(str(url)),
                    'example_url': url,
                }
            )

    parameters_df = pd.DataFrame(
        data=parameters,
        columns=['request_count', 'parameter', 'parameter_value_length', 'url_average_length', 'example_url']
    )
    del parameters

    parameters_df["parameter_value_length"] = pd.to_numeric(parameters_df["parameter_value_length"])
    parameters_df["url_average_length"] = pd.to_numeric(parameters_df["url_average_length"])
    parameters_df = parameters_df.groupby(['parameter'], as_index=False).agg({
        'request_count': 'count',
        'parameter_value_length': 'mean',
        'url_average_length': 'mean',
        'example_url': 'first',
    })
    parameters_df.sort_values(by=['request_count'], inplace=True, ascending=False)
    return parameters_df


if __name__ == '__main__':
    main()