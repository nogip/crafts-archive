import os


def collect_dirpaths(apps, root_dir, target_dir_name, extensions=None, find_all=True):
    result = []
    result.extend(internal_dir_paths(os.path.join(root_dir, target_dir_name)))
    for app in apps:
        result.extend(get_app_dirs(app, root_dir, target_dir_name, extensions, find_all))
    return result


def get_app_dirs(app_name, base_dir, template_dir_name, extensions=None, find_all=False):

    root_dir = os.path.join(base_dir, app_name)
    if not os.path.exists(root_dir):
        return []

    result = []
    paths = scan_dir_for_dirname(root_dir, template_dir_name, find_all)
    for template_dir_path in paths:
        internal = internal_dir_paths(template_dir_path, extensions)
        result.extend(internal)

    return result


def internal_dir_paths(root_dir, extensions=None):

    if not os.path.exists(root_dir):
        return []

    if not extensions:
        extensions = []

    elif not isinstance(extensions, list):
        extensions = [extensions, ]

    result = []

    has__files = has_files(root_dir, extensions)
    if has__files:
        result.append(root_dir)

    dir__paths = scan_dir(root_dir)
    if not dir__paths and not has__files:
        return []

    elif dir__paths:
        for path in dir__paths:
            result.extend(internal_dir_paths(path, extensions))

    return result


def scan_dir_for_dirname(root_dir, contract_name, find_all=False) -> list:
    internal_paths = []

    list_dir = os.listdir(root_dir)

    if contract_name in list_dir:
        internal_paths.append(os.path.join(root_dir, contract_name))

    if find_all or contract_name not in list_dir:
        for path in scan_dir(root_dir):
            internal_paths.extend(scan_dir_for_dirname(path, contract_name))

    return internal_paths


def scan_dir(root_dir):

    if not os.path.isdir(root_dir):
        return []

    dirs = []
    for item in os.listdir(os.path.normcase(root_dir)):

        dir_path = os.path.join(root_dir, item)
        if os.path.isdir(dir_path):
            dirs.append(dir_path)

    return dirs


def has_files(root_dir, extensions=None):
    if extensions and not isinstance(extensions, list):
        extensions = [extensions, ]

    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if not os.path.isfile(item_path):
            continue

        if extensions:
            for extension in extensions:
                if item.endswith(extension):
                    return True

        else:
            return True

    return False
