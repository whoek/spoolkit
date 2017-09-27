# -*- mode: python -*-

block_cipher = None

ADD_DATA = [
        ( 'templates', 'templates' ),        
        ( 'static', 'static' ),    
        ( 'templates\\admin', 'templates\\admin' ),
        ( 'templates\\admin\\model', 'templates\\admin\\model' )
        ]


a = Analysis(['spoolkit.py'],
             pathex=['C:\\data\\bitbucket\\spoolkit'],
             binaries=[],
             datas=ADD_DATA,
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
          name='spoolkit',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
