# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
        ('./icons/arrow_down.svg', 'icons'),
        ('./icons/minus.svg', 'icons'),
        ('./icons/plus.svg', 'icons'),
        ('./icons/tauno-plotter.svg', 'icons')
        ]

a = Analysis(['tauno-serial-plotter.py'],
             pathex=['/home/taunoerik/Documents/MyGitHub/tauno-serial-plotter/src'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='tauno-serial-plotter',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='tauno-serial-plotter')
