def change_paths(apps, base_dir):
    import re, os
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