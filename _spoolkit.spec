# -*- mode: python -*-

block_cipher = None


a = Analysis(['spoolkit.py'],
             pathex=['C:\\data\\bitbucket\\spoolkit'],
             binaries=[],
             datas=[
                ( 'C:\\data\\bitbucket\\spoolkit\\templates', 'templates' ),
                ( 'C:\\data\\bitbucket\\spoolkit\\templates\\admin', 'templates\\admin' ),
                ( 'C:\\data\\bitbucket\\spoolkit\\sql\\*.sql', 'sql' ),
                ( 'C:\\data\\bitbucket\\spoolkit\\static\\*.css', 'static' )
             ],             hiddenimports=[],
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
          exclude_binaries=True,
          name='spoolkit',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='spoolkit')
