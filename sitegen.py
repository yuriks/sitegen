import os
import os.path
import shutil

output_path = os.path.relpath("output")

cmd_prefix = '####!'

def path_for_root(path, root, cwd):
    tmp = path.replace('/', os.sep)
    tmp = os.path.normpath(tmp)
    if os.path.isabs(tmp):
        return os.path.join(root, tmp.lstrip(os.sep))
    else:
        return os.path.join(cwd, path)

def make_missing_dirs(fname):
    dir = os.path.split(fname)[0]
    if not os.path.exists(dir):
        os.makedirs(dir)

def process_file(fname):
    with open(fname, 'rU') as f:
        lines = []

        for l in f:
            if l.startswith(cmd_prefix):
                # Strip cmd_prefix and trailing whitespace
                l = l[len(cmd_prefix):].strip()
                if l.startswith('inc'):
                    inc_path = l.split(None, 1)[1]
                    fname_cwd = os.path.split(fname)[0]
                    lines += process_file(path_for_root(inc_path, os.getcwd(), fname_cwd))
                else:
                    print "Unknown command: %s" % l.split(None, 1)[0]
            else:
                lines.append(l)

    return lines

def handle_html_file(fname):
    dest_fname = os.path.join(output_path, fname)
    make_missing_dirs(dest_fname)

    lines = process_file(fname)
    with open(dest_fname, 'w') as f:
        f.writelines(lines)

def handle_misc_file(fname):
    dest_fname = os.path.join(output_path, fname)
    make_missing_dirs(dest_fname)

    shutil.copy2(fname, os.path.join(output_path, fname))

def handle_file(fname):
    name, ext = os.path.splitext(fname)
    if ext in ['.html']:
        print "Processing HTML: %s" % fname
        handle_html_file(fname)
    elif ext in ['.css', '.svg', '.png']:
        print "Processing raw file: %s" % fname
        handle_misc_file(fname)

def main():
    for root, dirs, files in os.walk('.'):
        # Removes all dotfiles, as well as the output directory.
        # Removing dotfiles handily removes several classes of unwanted files.
        # (repositories, vim swap files, etc.)
        dirs[:] = [name for name in dirs if not name.startswith('.') and os.path.relpath(os.path.join(root, name)) != output_path]
        files[:] = [name for name in files if not name.startswith('.')]

        for fn in files:
            handle_file(os.path.join(root, fn))

if __name__ == '__main__':
    main()
