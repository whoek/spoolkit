# -*- mode: python -*-

block_cipher = None


a = Analysis(['sap_spoolkit.py'],
             pathex=['C:\\data\\bitbucket\\spoolkit'],
             binaries=[],
             datas=[
                ( 'templates\\*.html', 'templates' )        
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='sap_spoolkit',
          debug=False,
          strip=False,
          upx=True,
          console=True )



