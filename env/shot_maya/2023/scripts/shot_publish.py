# Shot Publish
import os
import sys
import re
import shutil
sys.path.append("/home/rapa/git/pipeline/api_scripts")
sys.path.append("/usr/local/lib/python3.6/site-packages")
import subprocess
import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
from shotgun_api3 import Shotgun
# import shotgun_api3.Shotgun

try:
    from PySide6.QtWidgets import QApplication, QLabel, QTextEdit
    from PySide6.QtWidgets import QWidget, QPushButton, QMessageBox
    from PySide6.QtGui import *
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtCore import QFile
except:
    from PySide2.QtWidgets import QApplication, QLabel, QTextEdit
    from PySide2.QtWidgets import QWidget, QPushButton, QMessageBox
    from PySide2.QtUiTools import QUiLoader
    from PySide2.QtCore import QFile, Qt


class ShotPublish(QWidget):

    def __init__(self):
        super().__init__()
        
        self.make_ui()
        self.connect_sg()

        self.get_current_file_path()
        self.get_project()
        self.get_seq_name()
        self.get_seq_number()
        self.get_shot_task()
        self.get_shot_version()

        self.classify_task()

        self.ui.pushButton_shotpub.clicked.connect(self.get_root_nodes)


# UI 생성
    def make_ui(self):
        my_path = os.path.dirname(__file__)#/home/rapa/env/maya/2023/scripts        
        ui_file_path = my_path +"/shot_publish.ui"
        
        ui_file = QFile(ui_file_path)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        self.setWindowTitle("Shot Publish")
        ui_file.close()

    def connect_sg(self):
        URL = "https://4thacademy.shotgrid.autodesk.com"
        SCRIPT_NAME = "moomins_key"
        API_KEY = "gbug$apfmqxuorfqaoa3tbeQn"

        # self.sg = shotgun.Shotgun(URL,
        #                         SCRIPT_NAME,
        #                         API_KEY)
        self.sg = Shotgun(URL,
                                SCRIPT_NAME,
                                API_KEY)

# 현재 작업 중인 shot 파일의 경로
    def get_current_file_path(self): 
        self.current_file_path = cmds.file(query=True, sceneName=True)
        return self.current_file_path
# 경로를 통해 정보 가져오기    
    def get_project(self):
        split_file_path = self.current_file_path.split("/") #['', 'home', 'rapa', 'wip', 'Marvelous', 'seq', 'FCG', 'FCG_0010', 'lgt', 'wip', 'scenes', 'FCG_0010_light_v001.ma']
        project_name = split_file_path[4] #'Marvelous'
        self.ui.label_project.setText(project_name)
        return project_name
    
    def get_seq_name(self):
        split_file_path = self.current_file_path.split("/") #['', 'home', 'rapa', 'wip', 'Marvelous', 'seq', 'FCG', 'FCG_0010', 'lgt', 'wip', 'scenes', 'FCG_0010_light_v001.ma']
        seq_name = split_file_path[6] #FCG
        self.ui.label_seq_name.setText(seq_name)
        return seq_name

    def get_seq_number(self):
        split_file_path = self.current_file_path.split("/") #['', 'home', 'rapa', 'wip', 'Marvelous', 'seq', 'FCG', 'FCG_0010', 'lgt', 'wip', 'scenes', 'FCG_0010_light_v001.ma']
        seq_number = split_file_path[7] # FCG_0010
        self.ui.label_seq_number.setText(seq_number)
        return seq_number

    def get_shot_id(self):
        seq_num = self.get_seq_number()

        shot_filter = [["code", "is", seq_num]] # AFT_0010
        shot_field = ["id"]
        shot_entity = self.sg.find_one("Shot", filters=shot_filter, fields=shot_field)
        shot_id = shot_entity['id']
        return shot_id

    def get_shot_version(self):
        split_file_path = self.current_file_path.split("/") #['', 'home', 'rapa', 'wip', 'Marvelous', 'seq', 'FCG', 'FCG_0010', 'lgt', 'wip', 'scenes', 'FCG_0010_light_v001.ma']
        shot_version = split_file_path[-1] #FCG_0010_light_v001.ma
        p = re.compile('v\d{3}')
        p_data = p.search(shot_version)
        version = p_data.group() #v001
        self.ui.label_version.setText(version)
        return version

    def get_shot_task(self):
        split_file_path = self.current_file_path.split("/") #['', 'home', 'rapa', 'wip', 'Marvelous', 'seq', 'FCG', 'FCG_0010', 'lgt', 'wip', 'scenes', 'FCG_0010_light_v001.ma']
        user_task = split_file_path[8] #lgt
        return user_task



# 현재 작업의 task를 분리해서 각각의 클린업리스트 보여주고, export할 때 다른 함수 실행
    def classify_task(self):
        user_task = self.get_shot_task()
        print(f"현재 작업 Task는 {user_task}입니다.")

        # Matchmove : mb,      camera abc export + link    + sg status update + abc pub directory upload + sg undistortion size update
        # layout    : mb, abc, camera abc export + link    + sg status update + abc pub directory upload
        # Animation : mb, abc, camera abc export + link    + sg status update + abc pub directory upload
        # Lighting  : mb,             exr export + link    + sg status update + abc pub directory upload
                                                           # sg update는 export 관련 함수 실행한 후에 classify task 함수 안에서 따로 실행

        if user_task == 'mm': # Matchmove는 camera export + link + sg status update, abc pub directory upload, sg undistortion size update
            mm_clean_up_list = """
MatchMove팀 클린업리스트\n
- 카메라 트래킹 데이터 정리 및 최적화
- 3D 포인트 클라우드 정리
- 불필요한 트래킹 마커 제거
- 카메라 움직임 스무딩
- 렌즈 왜곡 보정
- 3D 지오메트리와 실사 영상의 정렬 확인
- 카메라 데이터 포맷 변환 및 내보내기
- 작업 파일 정리 및 문서화
            """
            self.ui.textEdit_shotcomment.setText(mm_clean_up_list)
            self.ui.pushButton_shotpub.clicked.connect(self.make_pub_path) # 폴더 생성
            self.ui.pushButton_shotpub.clicked.connect(self.export_mb)
            self.ui.pushButton_shotpub.clicked.connect(self.export_camera_alembic)

            self.ui.pushButton_shotpub.clicked.connect(self.link_camera) # rendercam 폴더에 카메라 링크
            self.ui.pushButton_shotpub.clicked.connect(self.open_folder)
            self.ui.pushButton_shotpub.clicked.connect(self.sg_status_update)
            self.ui.pushButton_shotpub.clicked.connect(self.sg_abc_pub_directory_update)
            self.ui.pushButton_shotpub.clicked.connect(self.sg_undistort_size_update)

        elif user_task == 'ly': # layout은 mb, abc, camera를 export + link, sg status update, abc pub directory upload
            layout_clean_up_list = """
Layout팀 클린업리스트\n
- 장면 구성 요소의 정리 및 최적화
- 객체 배치의 일관성 및 비율 조정
- 카메라 앵글 및 구도 검토
- 공간감과 깊이 표현의 정확성 확보
- 배경과 주요 요소 간의 조화로운 배치
- 애니메이션과 VFX 작업을 위한 여백 확보
- 불필요한 요소 및 지오메트리 제거
- 작업 파일 정리 및 문서화
            """ 
            self.ui.textEdit_shotcomment.setText(layout_clean_up_list)
            self.ui.pushButton_shotpub.clicked.connect(self.make_pub_path) # 폴더 생성
            self.ui.pushButton_shotpub.clicked.connect(self.export_mb)
            self.ui.pushButton_shotpub.clicked.connect(self.export_alembic)
            self.ui.pushButton_shotpub.clicked.connect(self.export_camera_alembic)

            self.ui.pushButton_shotpub.clicked.connect(self.link_camera)
            self.ui.pushButton_shotpub.clicked.connect(self.open_folder)
            self.ui.pushButton_shotpub.clicked.connect(self.sg_status_update)
            self.ui.pushButton_shotpub.clicked.connect(self.sg_abc_pub_directory_update)

        elif user_task == 'ani': # Animation은 mb, abc, camera를 export + link, sg status update, abc pub directory upload
            ani_clean_up_list = """
Animation팀 클린업리스트\n
- 키프레임 간 움직임 부드럽게 조정 및 타이밍 최적화
- 오버슈팅/언더슈팅 보정 및 동작의 연속성 확보
- 얼굴 표정과 립싱크 미세 조정
- 관절 변형 문제 해결 및 의상/헤어 시뮬레이션 개선
- 무게감과 균형 조정, 2차 모션 추가 및 개선
- 애니메이션과 카메라 움직임 동기화
- 리깅 관련 문제 수정 및 충돌 감지/해결
- 렌더링 최적화를 위한 애니메이션 조정
            """
            self.ui.textEdit_shotcomment.setText(ani_clean_up_list)
            self.ui.pushButton_shotpub.clicked.connect(self.make_pub_path) # 폴더 생성
            self.ui.pushButton_shotpub.clicked.connect(self.export_mb)
            self.ui.pushButton_shotpub.clicked.connect(self.export_alembic)
            self.ui.pushButton_shotpub.clicked.connect(self.export_camera_alembic)

            self.ui.pushButton_shotpub.clicked.connect(self.link_camera)
            self.ui.pushButton_shotpub.clicked.connect(self.open_folder)
            self.ui.pushButton_shotpub.clicked.connect(self.sg_status_update)
            self.ui.pushButton_shotpub.clicked.connect(self.sg_abc_pub_directory_update)

        elif user_task == 'lgt': # Lighting은 mb, abc, camera export + link, sg status update, abc pub directory upload
            lgt_clean_up_list = """
Lighting팀 클린업리스트\n
- 불필요한 라이트 제거 및 라이트 강도/색상 미세 조정
- 그림자 품질 개선 및 환경 조명(HDRI, GI) 최적화
- 불필요한 렌더 레이어 제거 및 렌더 패스 구조 정리
- 셰이더 및 텍스처 속성 미세 조정, 품질 확인
- 반사, 굴절, 앰비언트 오클루전 효과 개선
- 렌더 요소 간 일관성 확보 및 알파 채널/마스크 확인
- 볼류메트릭 라이팅, 발광 효과, 렌즈 플레어 정제
- 전체적인 렌더 설정 최적화 및 렌더 시간 단축
            """
            self.ui.textEdit_shotcomment.setText(lgt_clean_up_list)
            self.ui.pushButton_shotpub.setText("Publish")

            self.ui.pushButton_shotpub.clicked.connect(self.make_pub_path) # 폴더 생성
            self.ui.pushButton_shotpub.clicked.connect(self.export_mb)

            #수정
            self.ui.pushButton_shotpub.clicked.connect(self.export_exr)
            self.ui.pushButton_shotpub.clicked.connect(self.copy_folders)

            self.ui.pushButton_shotpub.clicked.connect(self.open_folder)
            self.ui.pushButton_shotpub.clicked.connect(self.sg_status_update)
            self.ui.pushButton_shotpub.clicked.connect(self.sg_pub_exr_directory_update)


        else: # user_task in ["mod", "lkd", "rig", "fx", "comp"]:
            QMessageBox.about(self, "경고", "'Shot Publish'는 maya를 사용하는 Shot 작업에서만 실행할 수 있습니다.\n현재 작업 중인 내용을 확인해주세요 ")



    def make_pub_path(self): # 'cache','scenes','images','sourceimages' 경로 생성
        if not self.current_file_path:
            QMessageBox.about(self, "경고", "파일이 저장되지 않았더나 열리지 않았습니다.")

        project = self.get_project() #Marvelous
        seq_name = self.get_seq_name() #FCG
        seq_number = self.get_seq_number() #FCG_0010
        task = self.get_shot_task() #lgt
        version = self.get_shot_version() #v001

        self.open_pub_path = f"/home/rapa/pub/{project}/seq/{seq_name}/{seq_number}/{task}/pub/"

        folder_list = ['cache','scenes','images','sourceimages']
        created_folders = []
        for folder in folder_list:
            folder_path = os.path.join(self.open_pub_path, folder, version)

            if not os.path.exists(folder_path): # 경로가 없을 때 폴더 생성
                try:
                    os.makedirs(folder_path, exist_ok=True)
                    created_folders.append(folder_path)

                except OSError as e: 
                    QMessageBox.about(self, "경고", f"경로 생성 중 오류 발생 : {str(e)}")
        print (f"{self.open_pub_path}하위의\n'cache','scenes','images','sourceimages'경로가 성공적으로 생성되었습니다.")

    def open_folder(self): # 생성된 폴더 오픈
        if hasattr(self, 'open_pub_path') and os.path.exists(self.open_pub_path):
            subprocess.call(["xdg-open", self.open_pub_path])
        else:
            QMessageBox.warning(self, "경고", "존재하지 않는 경로입니다.")



# Export
    def get_root_nodes(self): # 카메라를 제외한 최상위의 그룹 이름을 only_assemblies 리스트로 리턴
        """
        씬의 최상위 노드를 찾아서 only_assemblies 리스트에 넣는다
        """
        assemblies = cmds.ls(assemblies=True)
        camera_shapes = cmds.ls(cameras=True)
        cameras = cmds.listRelatives(camera_shapes, parent=True)
        only_assemblies = list(set(assemblies) - set(cameras))
        return only_assemblies

    def export_mb(self): # scenes/v001 생성, 카메라를 포함한 씬 전체를 export (완료)

        project = self.get_project() # Marvelous
        seq_name = self.get_seq_name() # FCG
        seq_number = self.get_seq_number() # FCG_0010
        task = self.get_shot_task() # lgt
        version = self.get_shot_version() # v001

        self.open_pub_path=f"/home/rapa/pub/{project}/seq/{seq_name}/{seq_number}/{task}/pub/"
        self.pub_path = os.path.join(self.open_pub_path, 'scenes', version)

        # mb 파일 경로
        mb_file_path = os.path.join(self.open_pub_path, 'scenes', version, f'{seq_number}_{task}_{version}.mb')

        # Validate
        if os.path.exists(mb_file_path):
            print (f'MB 파일 {mb_file_path}가 이미 존재합니다. Export를 취소합니다.')
            return

        try:
            cmds.file(rename=mb_file_path)
            cmds.file(mb_file_path, exportAll=True, type="mayaBinary", force=True) #mb 파일은 생성자체가 안됨. 오류... type="mayaBinary"
            print(f"MB 파일이 성공적으로 내보내졌습니다: {mb_file_path}")
        except Exception as e:
            print(f"MB 파일 내보내기 중 오류 발생: {str(e)}")
            error_msg_box = QMessageBox()
            error_msg_box.setIcon(QMessageBox.Critical)
            error_msg_box.setText(f"'{mb_file_path}'생성 중 오류 발생 : {str(e)}")
            error_msg_box.setWindowTitle("파일 내보내기 실패")
            error_msg_box.setStandardButtons(QMessageBox.Ok)
            error_msg_box.exec()      

    def export_alembic(self): # cache/v001이 생성, 카메라 제외한 abc export (완료)

        project = self.get_project() #Marvelous
        seq_name = self.get_seq_name() #FCG
        seq_number = self.get_seq_number() #FCG_0010
        task = self.get_shot_task() #lgt
        version = self.get_shot_version() #v001

        self.open_pub_path=f"/home/rapa/pub/{project}/seq/{seq_name}/{seq_number}/{task}/pub/"
        self.pub_path = os.path.join(self.open_pub_path, 'cache', version)

        # Alembic 파일 경로
        abc_file_path = os.path.join(self.open_pub_path, 'cache', version, f'{seq_number}_{task}_{version}.abc')

        # Validate
        if os.path.exists(abc_file_path):
            print (f'ABC 파일 {abc_file_path}가 이미 존재합니다. Export를 취소합니다.')
            return

        root_nodes = self.get_root_nodes()
        if not root_nodes:
            print ('내보낼 root 노드가 없습니다.')
            return
        cmds.select(root_nodes, replace=True)

        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)

        abc_export_cmd = '-frameRange {} {} -dataFormat ogawa '.format(start_frame, end_frame)
        for root in root_nodes:
            abc_export_cmd += '-root {} '.format(root)
        abc_export_cmd += '-file "{}"'.format(abc_file_path)

        try:
            cmds.AbcExport(j=abc_export_cmd)
            print (f'Alembic 파일이 성공적으로 Export 되었습니다.: {abc_file_path}')

        except Exception as e:
            print (f"Alembic Export 오류 발생 : {str(e)}")
            error_msg_box = QMessageBox()
            error_msg_box.setIcon(QMessageBox.Critical)
            error_msg_box.setText(f"'{abc_file_path}'생성 중 오류 발생 : {str(e)}")
            error_msg_box.setWindowTitle("파일 내보내기 실패")
            error_msg_box.setStandardButtons(QMessageBox.Ok)
            error_msg_box.exec()

    def export_camera_alembic(self): # cache/v001 안에 camera abc export (완료)
        # camera = self.get_camera_names() # camera1

        project = self.get_project() # Marvelous
        seq_name = self.get_seq_name() # FCG
        seq_number = self.get_seq_number() # FCG_0010
        task = self.get_shot_task() # lgt
        version = self.get_shot_version() # v001

        self.open_pub_path = f"/home/rapa/pub/{project}/seq/{seq_name}/{seq_number}/{task}/pub/"
        self.pub_path = os.path.join(self.open_pub_path,'cache',version)
        camera_file_path = os.path.join(self.open_pub_path,'cache',version,f'{seq_number}_{task}_cam.abc')

        # 카메라 노드만 선택
        camera_list = []
        camera_shapes = cmds.ls(type='camera')
        cameras = cmds.listRelatives(camera_shapes, parent=True)
        for camera in cameras:
            if camera in ["front", "top", "side", "persp"]:
                continue
            camera_list.append(camera)
        if len(camera_list) > 1:
            QMessageBox.about(self, "경고", "현재 씬에 카메라가 2개 이상입니다.\n현재 시퀀스용 카메라만 남겨주세요.")
            return
        camera1 = camera_list[0] # camera1

        # Alembic 내보내기 명령어 설정
        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)

        # Alemic export 명령어 생성
        abc_export_cmd = '-frameRange {} {} -dataFormat ogawa -root {} -file "{}"'.format(
        start_frame-10, end_frame+10, camera1, camera_file_path)

        print (abc_export_cmd)
        # Alembic 내보내기 실행
        try:
            cmds.AbcExport(j=abc_export_cmd)
            print (f'Alembic 파일이 성공적으로 Export 되었습니다.: {camera_file_path}')

        except Exception as e:
            print (f"Alembic Export 오류 발생 : {str(e)}")

        return camera_file_path
   
   ################################### 수정 #########################################


    def extract_version(self, file_path):
        """
        파일 경로에서 버전 번호를 추출합니다.
        """
        match = re.search(r'v(\d{3})', file_path)  # 'vXXX' 형식에서 숫자만 추출
        if match:
            return match.group(1)    # 패턴에 맞는 전체 문자열을 반환합니다.

    def set_image_size(self, width, height):
        """
        Maya 렌더 설정에서 이미지 크기를 변경합니다.

        :param width: 렌더링 이미지의 너비
        :param height: 렌더링 이미지의 높이
        """
        # 'defaultResolution' 노드에 접근합니다.
        default_resolution = 'defaultResolution'
        
        # 이미지 크기를 설정합니다.
        cmds.setAttr(f"{default_resolution}.width", width)
        cmds.setAttr(f"{default_resolution}.height", height)


    def export_exr(self):

        # Arnold 플러그인 로드
        if not cmds.pluginInfo('mtoa', query=True, loaded=True):
            cmds.loadPlugin('mtoa')
        
        # 마야 씬의 프레임 레인지 가져오기
        start_frame = cmds.playbackOptions(q=True, min=True)
        end_frame = cmds.playbackOptions(q=True, max=True)
        
        # Arnold 렌더러 설정
        cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
        cmds.setAttr("defaultRenderGlobals.startFrame", start_frame)
        cmds.setAttr("defaultRenderGlobals.endFrame", end_frame)

        # 렌더링에 사용할 카메라 설정
        camera = self.get_camera_names()
        print(camera)
        if cmds.objExists(camera):
            cmds.setAttr(f"{camera}.renderable", 1)  # 렌더 카메라 활성화 (1은 활성화, 0은 비활성화)

        # 현재 열려 있는 파일의 경로를 가져옵니다.

        current_file = cmds.file(q=True, sceneName=True)
        images_path = current_file.replace("scenes", "images")

        file_name = os.path.dirname(images_path)
        pub_path = file_name.replace("wip","pub")
        file_path = pub_path.split('/')[:-1]
        base_folder = '/'.join(file_path)

        
        #언디스토션 사이즈
        image_size = self.get_image_plane_coverage()
        camera_names = self.get_camera_names()
        
        image_size_width = int(image_size[camera_names]["width"]) 
        image_size_height = int(image_size[camera_names]["height"]) 
        
        #이미지 사이즈 수정
        self.set_image_size(image_size_width, image_size_height)        
        
        
        # 파일 경로에서 버전 번호 추출
        version = self.extract_version(current_file)
        ver = f"v{version}"
        # 버전 폴더 생성
        self.version_folder = os.path.join(base_folder, ver)
        #/home/rapa/pub/Moomins/seq/AFT/AFT_0010/lgt/pub/images/v002
        
        # 버전 폴더가 존재하지 않으면 생성
        if not os.path.exists(self.version_folder):
            os.makedirs(self.version_folder)

        # 모든 렌더 레이어를 렌더링 가능하도록 설정
        render_layers = cmds.ls(type="renderLayer")
        for layer in render_layers:
            if cmds.getAttr(layer + ".renderable") == 1:  # 렌더링 가능한 레이어만 선택
                cmds.editRenderLayerGlobals(currentRenderLayer=layer)

                # 출력 경로 설정 - `<RenderLayer>` 토큰 추가
                output_path = os.path.join(self.version_folder, "<RenderLayer>/<Scene>")
                cmds.setAttr("defaultRenderGlobals.imageFilePrefix", output_path, type="string")

                # Arnold 이미지 형식 설정
                cmds.setAttr("defaultArnoldDriver.aiTranslator", "exr", type="string")  # EXR 형식으로 설정
                cmds.setAttr("defaultArnoldDriver.colorManagement", 1)  # ACES 색상 관리 활성화

                # 렌더 옵션 설정
                cmds.setAttr("defaultRenderGlobals.imageFormat", 7)  # EXR 형식
                cmds.setAttr("defaultRenderGlobals.animation", 1)  # 애니메이션 활성화
                cmds.setAttr("defaultRenderGlobals.useFrameExt", 1)  # 파일 이름에 프레임 포함
                cmds.setAttr("defaultRenderGlobals.outFormatControl", 0)  # 기본 포맷 제어 비활성화
                cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)  # 파일 확장자 앞에 프레임 번호 삽입
                cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)  # 프레임 번호에 대해 패딩 4로 설정

                # 프레임 설정
                render_first_frame = int(start_frame)
                render_last_frame = int(end_frame)
                
                # 각 프레임별로 렌더링
                for frame in range(render_first_frame, render_last_frame + 1):
                    cmds.currentTime(frame)  # 프레임 설정
                    # 렌더링 수행 (렌더 뷰 없이)
                    cmds.arnoldRender(cam=camera, seq=(frame, frame), x=image_size_width, y=image_size_height)

                    
    def extract_version_folder_name(self,folder_name):
        """
        폴더 이름에서 버전 번호를 추출합니다.
        버전 번호는 'vXXX' 형식으로 되어 있다고 가정합니다.
        """
        match = re.search(r'v(\d{3})', folder_name)
        if match:
            return int(match.group(1))  # 정수로 변환하여 반환         
        


    def get_version_folders(self, base_folder, file_name):
        """
        현재 파일 이름에서 버전 번호를 추출하고, 현재 버전과 해당 버전에서 -1을 적용한 버전의 폴더 경로를 생성합니다.
        """
        current_version = self.extract_version_folder_name(file_name)
        if current_version is not None:
            current_version_folder = os.path.join(base_folder, f"v{current_version:03d}")
            previous_version_folder = os.path.join(base_folder, f"v{current_version - 1:03d}")
            
            return current_version_folder, previous_version_folder


    def get_file_paths(self):
        """
        현재 열려 있는 마야 파일의 경로를 기반으로 현재 버전과 이전 버전 경로를 반환합니다.
        """
        # 현재 파일 및 경로 정보 가져오기
        current_file = cmds.file(q=True, sceneName=True)  # 마야에서 현재 열려 있는 파일의 경로를 가져옵니다.
        images_path = current_file.replace("scenes", "images")  # "scenes"를 "images"로 대체
        pub_path = images_path.replace("wip", "pub")

        file_name = os.path.basename(pub_path)  # 파일 이름만 추출
        file_path = os.path.dirname(pub_path)  # 파일의 디렉터리 이름을 가져옵니다.
        
        base_folder = os.path.dirname(file_path)  # 경로를 슬래시로 분할하고, 마지막 부분을 제외

        # 현재 버전(v002) 및 이전 버전 경로(v001)
        current_version_folder, previous_version_folder = self.get_version_folders(base_folder, file_name)
        return current_version_folder, previous_version_folder


    def copy_folders(self):

        #maya에서 경로가져오기
        dest_dir, src_dir = self.get_file_paths()

        # 현재 버전이 v001인 경우, 복사를 수행하지 않음
        current_version = self.extract_version(os.path.basename(dest_dir))
        if current_version == 1:
            print("복사 실행하지 않음")
            return

        # 대상 디렉터리가 존재하지 않으면 생성
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # 소스 디렉터리의 각 항목에 대해 반복
        for item in os.listdir(src_dir):
            src_path = os.path.join(src_dir, item)
            dest_path = os.path.join(dest_dir, item)

            # 항목이 디렉터리인지 확인
            if os.path.isdir(src_path):
                # 대상 경로에 같은 이름의 디렉터리가 이미 존재하는지 확인
                if not os.path.exists(dest_path):
                    # 존재하지 않으면 폴더 복사
                    shutil.copytree(src_path, dest_path)

   ################################### 수정 #########################################




    def link_camera(self): # 완료
        print("****************** link camera")
        project = self.get_project()
        seq_name = self.get_seq_name()
        seq_number = self.get_seq_number()
        task = self.get_shot_task()

        seq_cam_folder_path = f"/home/rapa/pub/{project}/seq/{seq_name}/{seq_number}/rendercam"
        seq_cam_file_name = f"{seq_number}_cam.abc" # OPN_0010_cam.abc
        seq_cam_path = os.path.join(seq_cam_folder_path, seq_cam_file_name)
        # print(f"*****************{seq_cam_folder_path}")
        # print(f"*****************{seq_cam_file_name}")
        # print(f"*****************{seq_cam_path}")
        # *****************/home/rapa/pub/Moomins/seq/AFT/AFT_0010/rendercam
        # ***************** AFT_0010_cam.abc
        # *****************/home/rapa/pub/Moomins/seq/AFT/AFT_0010/rendercam/AFT_0010_cam.abc

        print("폴더를 만들어라")
        if not os.path.exists(seq_cam_folder_path): # rendercam이 없으면 경로 생성
            os.makedirs(seq_cam_folder_path) # 폴더 생성

        # Rendercam에 Link
        task_list = ["mm","ly","ani"]
        print("-----------------------dsfkldjfsdfljk")
        for task in task_list:
            cam_path = f"/home/rapa/pub/{project}/seq/{seq_name}/{seq_number}/{task}/pub/cache"
            cam_name = f"{seq_number}_{task}_cam.abc" # OPN_0010_ani_cam.abc
            cam_full_path = os.path.join(cam_path, cam_name)

            if os.path.exists(cam_full_path):
                os.system(f"ln -s {cam_full_path} {seq_cam_path}") # ln -s 원본경로 심볼릭경로
                print(f"{task} 카메라를 rendercam에 링크 완료했습니다!")



### Backend (효은)
    def get_task_id(self): # 완료
        # seq_num_id 구하기
        seq_num = self.get_seq_number()
        seq_filter = [["code", "is", seq_num]] # 현재 작업 중인 시퀀스 넘버 ex.OPN_0010
        seq_field = ["id"]
        seq_info = self.sg.find_one("Shot", filters=seq_filter, fields=seq_field) # {'type': 'Asset', 'id': 1789}
        seq_num_id = seq_info["id"]
        print(f"seq_num_id 찾기 : {seq_num_id}")

        # step_id 찾기
        step_name = self.get_shot_task() # lgt, ly 등
        step_info = self.sg.find_one("Step",[["code", "is", step_name]], ["id"])
        step_id = step_info["id"]
        print(f"step id 찾기 : {step_id}")

        # seq_num_id, step_id 조건에 맞는 task id 찾기
        task_filter = [
            ["entity", "is", {"type": "Shot", "id": seq_num_id}],
            ["step", "is", {"type": "Step", "id": step_id}]
        ]
        task_field = ["id"]
        task_info = self.sg.find_one("Task", filters=task_filter, fields=task_field)
        task_id = task_info["id"]
        print(f"task id 찾기 : {task_id}")

        return task_id

    def sg_status_update(self): # 완료
        print("sg_status_update 함수 실행")

        task_id = self.get_task_id()
        self.sg.update("Task", task_id, {"sg_status_list" : "pub"})

        print(f"Task 엔티티에서 {task_id}의 status를 pub으로 업데이트합니다.")

    def sg_abc_pub_directory_update(self): # 완료
        print("pub된 abc 파일의 경로를 pub file directory 필드에 업로드합니다.")
        task_id = self.get_task_id()
        camera_path = self.export_camera_alembic()
        # /home/rapa/pub/Moomins/seq/AFT/AFT_0010/lgt/pub/cache/v001/AFT_0010_lgt_cam.abc

        self.sg.update("Task", task_id, {"sg_description" : camera_path})

    def sg_pub_exr_directory_update(self): # export_exr함수 경로 확인 필요
        print("pub된 exr 파일의 경로를 pub file directory 필드에 업로드합니다.")
        task_id = self.get_task_id()
        exr_path  = self.version_folder()
        # print(exr_path)

        self.sg.update("Task", task_id, {"sg_description" : exr_path})



    def get_camera_names(self): # 완료
        """
        마야 안에 기본 카메라는 제외한 카메라의 이름을 가져오는 코드
        """
        # 기본 카메라 이름 리스트
        default_cameras = ["front", "persp", "side", "top"]

        # 모든 카메라 노드 찾기
        all_cameras = cmds.ls(type='camera', long=True)

        # 카메라의 부모 노드 이름을 가져옵니다.
        camera_names = []
        for camera in all_cameras:
            parent_node = cmds.listRelatives(camera, parent=True, fullPath=True)
            if parent_node:
                camera_names.append(parent_node[0])

        # 기본 카메라 이름을 제외합니다.
        filtered_cameras = []
        for camera_name in camera_names:
            short_name = camera_name.split('|')[-1]
            if short_name not in default_cameras:
                filtered_cameras.append(short_name)

        if filtered_cameras:
            # 필터링된 카메라 이름들을 문자열로 결합합니다.
            camera_names_str = ', '.join(filtered_cameras)
            print("아웃라이너에서 기본 카메라를 제외한 모든 카메라가 선택되었습니다.")

            # 카메라 이름을 문자열로 반환합니다.
            return camera_names_str

    def sg_undistort_size_update(self): # mm의 카메라에서 나온 undistortion size를 sg에 업데이트 합니다. (완료)
        undistortion_dict = self.get_image_plane_coverage()
        print(undistortion_dict)
        # {'camera1': {'width': 2040, 'height': 1220}}
        camera_names = self.get_camera_names()
        print(camera_names) # camera1
        
        undistortion_width = str(undistortion_dict[camera_names]["width"]) # 2040 (스트링)
        undistortion_height = str(undistortion_dict[camera_names]["height"]) # 1220 (스트링)

        shot_id = self.get_shot_id()
        print(shot_id) # 1353

        # SG Shot 엔티티의 undistortion size 필드에 각각 업로드
        self.sg.update("Shot", shot_id, {"sg_undistortion_width" : undistortion_width,
                                         "sg_undistortion_height" : undistortion_height})

    def get_image_plane_coverage(self): # 완료
        """
        카메라의 이미지플랜을 검색하고, coverage X, Y를 가져온다.
        가져온 카메라이름과 coverage를 이중 딕셔너리로 묶는다
        ex : {'OPN_0010': {'width': 3000, 'height': 2145}}
        """
        # 카메라 이름가져오기
        result = self.get_camera_names()
        split_name = result.split("_")
        seq_name = split_name[:2]
        camera_name = "_".join(seq_name)

        # 카메라의 shape 노드 찾기
        camera_undistortion = {}
        shapes = cmds.listRelatives(result, shapes=True, type='camera')
        camera_shape = shapes[0]

        # 카메라의 image plane 찾기
        image_planes = cmds.listConnections(camera_shape, type='imagePlane')#객체속의 연결되어 있는 다른노드들을 탐색합나다.
        image_plane = image_planes[0]

        # coverageX와 coverageY 값 가져오기
        try:
            coverage_x = cmds.getAttr(f"{image_plane}.coverageX")
            coverage_y = cmds.getAttr(f"{image_plane}.coverageY")
            camera_undistortion[camera_name] = {
                "width" : coverage_x,
                "height" : coverage_y
            }
            return camera_undistortion

        except Exception as e:
            print(f"  이미지 플레인 속성 값을 가져오는 중 오류가 발생했습니다: {e}")



if __name__ == "__main__":
    if not QApplication.instance():
        app = QApplication(sys.argv)
    win = ShotPublish()
    win.show()
    app.exec()