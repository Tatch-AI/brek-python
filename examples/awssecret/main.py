from brek import DefaultLoaders, GetConfig, SetLoaders


def main() -> None:
    SetLoaders(DefaultLoaders())
    conf = GetConfig()
    print(conf["secret"])


if __name__ == "__main__":
    main()
