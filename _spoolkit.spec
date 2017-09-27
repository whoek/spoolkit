# -*- mode: python -*-

block_cipher = None

ADD_DATA = [
        ( 'templates', 'templates' ),        
        ( 'static', 'static' ),    
        ( 'static\\bootstrap-3.3.7\\css', 'static\\bootstrap-3.3.7\\css' ),    
        ( 'static\\bootstrap-3.3.7\\fonts', 'static\\bootstrap-3.3.7\\fonts' ),    
        ( 'static\\bootstrap-3.3.7\\js', 'static\\bootstrap-3.3.7\\js' ),    
        ( 'static\\datatables-1.10.16\\css', 'static\\datatables-1.10.16\\css' ),    
        ( 'static\\datatables-1.10.16\\images', 'static\\datatables-1.10.16\\images' ),    
        ( 'static\\datatables-1.10.16\\js', 'static\\datatables-1.10.16\\js' ),    
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
