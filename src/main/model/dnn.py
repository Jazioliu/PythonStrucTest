from utility import logger

def main():
    LOGGER.info('hello world')

if __name__ == '__main__':
    LOGGER = logger.init_logger('download.log')
    main()
