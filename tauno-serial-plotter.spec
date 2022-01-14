# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

added_files = [
        ('./src/icons/arrow_down.svg', './icons/'),
        ('./src/icons/minus.svg', './icons/'),
        ('./src/icons/plus.svg', './icons/'),
        ('./src/icons/tauno-plotter.svg', './icons/'),
        ('./src/icons/tauno-plotter.png', './icons/'),
        ('./src/icons/tauno-plotter.ico', './icons/'),
        
        ]

a = Analysis(['src\\tauno-serial-plotter.py'],
             pathex=[],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
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
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='tauno-serial-plotter')
