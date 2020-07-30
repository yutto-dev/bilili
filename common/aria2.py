import os
import subprocess


class Aria2():
    def __init__(self, aria2_path='aria2c', show_progress=False):
        self.show_progress = show_progress
        assert subprocess.run([aria2_path], stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE).returncode == 1, "请配置正确的 aria2 路径"
        self.path = os.path.normpath(aria2_path)
        tmp_dir = os.path.join(os.path.dirname(aria2_path), "tmp")
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        self.tmp_dir = os.path.normpath(tmp_dir)

    def exec(self, params):
        """ 调用 aria2 """

        if self.show_progress:
            out_pipe = None
        else:
            out_pipe = subprocess.PIPE

        cmd = [self.path]
        cmd.extend(params)

        return subprocess.run(cmd, stdout=out_pipe, stderr=out_pipe)

    def download_video_list(self, video_list, dirname):
        input_file = os.path.join(self.tmp_dir, "aria2.in")

        with open(input_file, "w") as f:
            for video in video_list:
                f.write(
f'''{video["url"]}
    dir={dirname}
    out={video["filename"]}
    referer=https://www.bilibili.com
    user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36
''')

        command = [
            "aria2c",
            "-i", input_file,
        ]
        self.exec(command)
        os.remove(input_file)

    def download(self, url, filepath):
        dirname, filename = os.path.split(filepath)
        command = [
            "aria2c", url,
            "-d", dirname,
            "-o", filename,
            "--referer", "https://www.bilibili.com",
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36"
        ]
        self.exec(command)


