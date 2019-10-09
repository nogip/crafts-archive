import os

directory = input('Path to .opus files >> ')
out_dir = os.path.join(directory, 'opus_decoded_files')

dec_path = input('Path to .opus decoder >> ')
os.chdir(dec_path)
decoder = 'opusdec.exe'

dec_command = decoder + ' --quiet "{inp}" "{out}"'

print(directory)
print(out_dir)

if not os.path.exists(out_dir):
        os.mkdir(out_dir)

print('\n=== START DECODE ===')
print('WORDIR: ', directory)
print('OUTPUT DIR: ', out_dir)

for filename in os.listdir(directory):
    if filename.endswith('.opus'):
        inp_fp = os.path.join(directory, filename)
        filename = filename.split('.')[0] + '.wav'
        
        out_fp = os.path.join(out_dir, 'dec_' + filename)
        cmd = dec_command.format(inp=inp_fp, out=out_fp)
        print('Decoding ', out_fp)
        os.system(cmd)
print('+++ All files have decoded +++')
print('=== END DECODE ===')

    
