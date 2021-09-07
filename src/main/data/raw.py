import click
import requests

from utility import logger


@click.command()
@click.argument('url')
@click.argument('filename', type=click.Path())
def download_file(url, filename):
    LOGGER.info('Downloading from %s to %s', url, filename)

    response = requests.get(url)

    with open(filename, 'wb') as ofile:
        ofile.write(response.content)

    LOGGER.info('Done')


def main():
    download_file(None, None)


if __name__ == '__main__':
    LOGGER = logger.init_logger('raw.log')
    main()
