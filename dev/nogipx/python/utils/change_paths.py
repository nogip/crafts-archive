import re, os, shutil


def move_templates(apps, base_dir):
    if not os.path.exists(base_dir):
        return False

    root_template_dir = os.path.join(base_dir, 'templates')

    if not os.path.exists(root_template_dir):
        return False

    for t_appname in os.listdir(root_template_dir):

        if t_appname not in apps:
            return False

        t_appname = os.path.join(root_template_dir, t_appname)
        if not os.path.exists(t_appname) or not os.path.isdir(t_appname):
            return False

        app_template_dir = os.path.join(base_dir, t_appname, 'templates')
        if not os.path.exists(app_template_dir):
            os.mkdir(app_template_dir)

        for template in os.listdir(t_appname):
            template_old_path = os.path.join(root_template_dir, t_appname, template)
            template_new_path = os.path.join(app_template_dir, template)
            if template.endswith('.html'):
                status = shutil.move(template_old_path, template_new_path)
                print('[+] Moving {} :: {}'.format(status, template_new_path))


def change_paths(apps, base_dir):
    move_templates(apps, base_dir)
    codec = "utf-8"
    read_t = 'r'
    write_t = 'w'
    for app in apps:
        view_path = os.path.join(base_dir, app, 'views.py')
        if os.path.exists(view_path):
            with open(view_path, read_t, encoding=codec) as vr:
                content_v = vr.read()
                content_v = re.sub("render\(request, '[\w]*/", "render(request, '", content_v)
                content_v = re.sub('render\(request, "[\w]*/', 'render(request, "', content_v)

            with open(view_path, write_t) as vw:
                if vw.write(content_v):
                    print("[+] Refactored view :: {}".format(view_path))

        else:
            print("[-] View does not exists :: {}".format(view_path))

        template_dir = os.path.join(base_dir, app, 'templates')
        if os.path.exists(template_dir):

            for template in os.listdir(template_dir):

                template_path = os.path.join(template_dir, template)
                if os.path.exists(template_path):

                    with open(template_path, read_t, encoding=codec) as tr:
                        content_t = tr.read()
                        content_t = re.sub('\{% include "[\w]*/', '{% include "', content_t)
                        content_t = re.sub("\{% include '[\w]*/", "{% include '", content_t)

                    with open(view_path, write_t) as tw:
                        tw.write(content_t)
                        print("[+] Refactored template :: {}".format(template_path))

                else:
                    print("[-] Template does not exists :: {}".format(template_path))