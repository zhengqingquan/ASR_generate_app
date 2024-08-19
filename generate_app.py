#!/usr/bin/env python
#coding=utf-8

# @File: generate_app.py
# @Auther: zhengqingquan
# @Create: 2024/07/18
# @Update: 2024/07/19
# @Version: 1.0.1
# @Brief: Based on ASR platform code, it is possible to automatically generate Python scripts for the APP.
# @Instructions: Place the script in the root directory, modify the name of the app you need, and then execute it. And open the corresponding macro control.

import os
import sys
import re
import argparse
import logging
from pathlib import Path

def get_element_value(element):
    version_pattern = re.compile(rf"^# {element}:\s*(.*)$", re.MULTILINE)
    try:
        with open(__file__, 'r', encoding='utf-8') as file:
            content = file.read()
            match = version_pattern.search(content)
            if match:
                return match.group(1)
            else:
                return r'unkonw.'
    except FileNotFoundError:
        return r'unkonw.'

def insert_text_fun(file_name, pattern, insert_text, position):
    try:
        # 读取文件内容
        with open(file_name, 'r', encoding='utf-8') as file:
            # 插入内容已经存在
            if insert_text in file.read():
                return logging.info(f'Content repetition:{insert_text}')
            # 重置文件读取指针位置
            file.seek(0)
            lines = file.readlines()

        # 寻找匹配的位置
        match_found = False
        for i in range(len(lines)):
            if pattern in lines[i]:
                match_found = True
                lines.insert(i + position, insert_text)
                break

        # 未找到匹配内容。
        if not match_found:
            return logging.info(f'{file_name} no match found for pattern: {pattern}')

        # 写入文件
        with open(file_name, 'w') as file:
            file.writelines(lines)
    except FileNotFoundError:
        logging.error(f"File {file_name} not exist!")

def insert_func_end_fun(file_name, pattern_head, pattern_end, insert_text, position):
    try:
        # 读取文件内容
        with open(file_name, 'r') as file:
            # 插入内容已经存在
            if insert_text in file.read():
                return logging.info(f'Content repetition:{insert_text}')
            # 重置文件读取指针位置
            file.seek(0)
            lines = file.readlines()

        # 找到匹配行的位置
        match_found_pattern_head = False
        match_found_pattern_end = False
        for i in range(len(lines)):
            # 寻找匹配的开头
            if pattern_head in lines[i]:
                match_found_pattern_head = True
            # 已经找到匹配开头的情况下，寻找匹配的结尾
            if match_found_pattern_head and pattern_end in lines[i]:
                match_found_pattern_end = True
                lines.insert(i + position, insert_text)
                break

        # 未找到匹配内容。
        if not match_found_pattern_head:
            return logging.info(f'{file_name} no match found for pattern: {pattern_head}')
        if not match_found_pattern_end:
            return logging.info(f'{file_name} no match found for pattern: {pattern_end}')

        # 将修改后的内容写回文件
        with open(file_name, 'w') as file:
            file.writelines(lines)
    except FileNotFoundError:
        logging.error(f"File {file_name} not exist!")

def insert_file_end(file_name, insert_text):
    try:
        # 读取文件内容
        with open(file_name, 'r') as file:
            # 插入内容已经存在
            if insert_text in file.read():
                return logging.info(f'Content repetition:{insert_text}')

        # 在文件末尾追加文本
        with open(file_name, 'a') as file:
            file.write(insert_text)
    except FileNotFoundError:
        logging.error(f"File {file_name} not exist!")

def add_configuration_items():

    file_name = root_path.joinpath(r'evb/src/gui/Kconfig')

    pattern = r'menu "mUI app configurations"'

    insert_text = f'''
config {app_configuration_name}
	bool "enable {app_name} app"
	default n
	help
	  Select this option if you want to support {app_name}.
'''

    insert_text_fun(file_name, pattern, insert_text, 1)

def modify_cmake_file():

    file_name = root_path.joinpath(r'evb/src/gui/mgapollo/CMakeLists.txt')

    insert_text = f'''
if (DEFINED {app_macro_name})
    file(GLOB {app_name}_cpp_files   RELATIVE ${{CMAKE_CURRENT_SOURCE_DIR}}
        apps/{app_name}/src/*.cpp
    )
    set (library_cpp_files ${{library_cpp_files}} ${{{app_name}_cpp_files}})
endif()
'''

    pattern_head = r'file(GLOB library_cpp_files   RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}'
    pattern_end = r')'

    insert_func_end_fun(file_name, pattern_head, pattern_end, insert_text, 1)

def modify_rules_cmake_file():

    file_name = root_path.joinpath(r'evb/src/gui/mgapollo/rules.cmake')

    pattern_head = r'set(apollo_app_dirs'
    pattern_end = r')'

    insert_text1 = f'''
if (DEFINED {app_macro_name})
set (apollo_app_dirs
    ${{apollo_app_dirs}}
    {app_name.lower()}
)
endif()
'''

    insert_text2 = f'''
if (DEFINED {app_macro_name})
list(APPEND mgapollo_head_files
					"${{__G_MG_SIMULATOR_GEN_DIR}}/mgapollo/apps/{app_file_name}/include"
)
endif()
'''

    insert_func_end_fun(file_name, pattern_head, pattern_end, insert_text1, 1)

    insert_file_end(file_name, insert_text2)

def add_respkg_id():

    file_name = root_path.joinpath(r'evb/src/gui/mgapollo/apps/include/appcommoninclue.h')

    pattern_head = r'enum  _RES'
    pattern_end = r'//TODO'

    insert_text = f'''\
#ifdef {app_macro_name}
	RES_PKG_{app_name.upper()}_ID,
#endif
'''

    insert_func_end_fun(file_name, pattern_head, pattern_end, insert_text, 0)

def create_source_file():

    app_res_h=f'''\
#ifndef __NGUX_{app_name.upper()}_RES_H__
#define __NGUX_{app_name.upper()}_RES_H__

#include "sys_res.h"
#include "appwithbar.h"
#include "{app_h_file_name}.h"

#define RESPKGID      RPKG_{app_name}
#define RESID(name)   R_{app_name}_##name

#include "resdefines.head.h"
#include "{res_c_file_name}.res.c"
#include "resundefines.h"

#include "resdefines.name.h"
#include "{res_c_file_name}.res.c"
#include "resundefines.h"

#undef RESID
#undef RESPKGID

#endif  /* __NGUX_{app_name.upper()}_RES_H__ */
'''

    app_app_h=f'''\
#ifndef __NGUX_{app_name.upper()}_H__
#define __NGUX_{app_name.upper()}_H__

#include "ngux.h"
#include "appwithbar.h"

USE_NGUX_NAMESPACE

DECLARE_APP_FACTORY({app_name})

/**
 * @brief client
 */
enum {{
    {app_name.upper()}_CLIENT_BEGIN = APP_CLIENT_MAX,
    {app_name.upper()}_CLIENT_MAIN,
    {app_name.upper()}_CLIENT_MAX,
}};

/**
 * @brief event
 */
enum {{
    {app_name.upper()}_CMD_BEGIN = APP_CMD_MAX,
    {app_name.upper()}_CMD_ENTER,
    {app_name.upper()}_CMD_MENU,
    {app_name.upper()}_CMD_CLEAR,
    {app_name.upper()}_CMD_SAVE,
    {app_name.upper()}_CMD_BACK,
    {app_name.upper()}_CMD_MAX
}};

/**
 * @brief {app_name} APP Class.
 */
class {app_name} : public AppWithBar
{{
    DECLARE_CONTROLLER_CLIENTS

    public:
        {app_name}();
        ~{app_name}();

    private:
        void onCreate(ContextStream* contextstream, Intent* intent);
}};

#endif /* __NGUX_{app_name.upper()}_H__ */
'''

    app_client_h=f'''\
#ifndef __NGUX_{client_h_file_name.upper()}_H_
#define __NGUX_{client_h_file_name.upper()}_H_

#include "ngux.h"
#include "appwithbar.h"

USE_NGUX_NAMESPACE

class {app_client_class_name} : public AppClient
{{
    DECLARE_VIEWCONTEXT

    public:
        {app_client_class_name}(Controller* owner, NGInt view_id, View *parent, NGParam param1, NGParam param2);
        ~{app_client_class_name}();

    private:
        NGBool onKey(NGInt keyCode, KeyEvent* event);
        NGUInt onControllerCommand(NGUInt cmd_id, NGParam param1, NGParam param2);
        void active();
        void inactive();
}};

#endif /* __NGUX_{client_h_file_name.upper()}_H_ */
'''

    app_res_cpp=f'''\
#include "ngux.h"
#include "{res_h_file_name}.h"

USE_NGUX_NAMESPACE

#define RESPKGID      RPKG_{app_name}
#define RESID(name)   R_{app_name}_##name

#include "resdefines.source.h"
#include "{res_c_file_name}.res.c"
#include "resundefines.h"

#include "resdefines.init.h"
#include "{res_c_file_name}.res.c"
#include "resundefines.h"

#undef RESID
#undef RESPKGID
'''

    app_app_cpp=f'''\
#include "ngux.h"
#include "{app_h_file_name}.h"
#include "{client_h_file_name}.h"
#include "{res_h_file_name}.h"

{app_class_name}::{app_class_name}() :AppWithBar(true)
{{
    FRRegister_{app_name}_resource();
}}

{app_class_name}::~{app_class_name}()
{{

}}

void {app_class_name}::onCreate(ContextStream* contextStream, Intent* intent)
{{
    AppWithBar::onCreate(contextStream, intent);
    AppWithBar::setFullScreen(false);
    showView({app_name.upper()}_CLIENT_MAIN, 0, 0);
}}

BEGIN_CONTROLLER_CLIENTS({app_class_name})
    CONTROLLER_CLIENT({app_name.upper()}_CLIENT_MAIN, {app_client_class_name})
END_CONTROLLER_CLIENTS_EX(AppWithBar)

BEGIN_DEFINE_APP({app_class_name})
    APP_SET(name, "{app_name.lower()}")
    APP_SET(position, POS_HIDE)
END_DEFINE_APP
'''

    app_client_cpp=f'''\
#include "ngux.h"
#include "{res_h_file_name}.h"
#include "{app_h_file_name}.h"
#include "{client_h_file_name}.h"

USE_NGUX_NAMESPACE

BEGIN_SETVIEW({app_client_class_name})
END_SETVIEW

BEGIN_GETHANDLE({app_client_class_name})
END_GETHANDLE

{app_client_class_name}::{app_client_class_name}(Controller*owner, int view_id, View *parent, NGParam param1, NGParam param2)
    :AppClient(owner, view_id, parent)
{{
    m_baseView = CreateViewFromRes(R_{app_name}_ui_{app_client_class_name.lower()}_main, parent, this , NULL);
}}

{app_client_class_name}::~{app_client_class_name}()
{{

}}

void {app_client_class_name}::active()
{{
    AppClient::active();
}}

void {app_client_class_name}::inactive()
{{
    AppClient::inactive();
}}

bool {app_client_class_name}::onKey(int keyCode, KeyEvent* event)
{{
    return DISPATCH_CONTINUE_MSG;
}}

NGUInt {app_client_class_name}::onControllerCommand(NGUInt cmd_id, NGParam param1, NGParam param2)
{{
    switch (cmd_id)
    {{
        case {app_name.upper()}_CMD_ENTER:
        {{
            break;
        }}
        case {app_name.upper()}_CMD_CLEAR:
        {{
            break;
        }}
        default:
        {{
            break;
        }}
    }}

    return DISPATCH_STOP_MSG;
}}
'''

    app_res_c=f'''\
begin_respkg({app_name}, RES_PKG_{app_name.upper()}_ID)

    //image resource
    begin_image_res()
    end_image_res

    //drawable resource
    begin_dr_res
    end_dr_res

    //drawableset resource
    begin_drset_res
    end_drset_res

    //ui resource
    begin_uis
        begin_ui_res({app_client_class_name.lower()}_main)
            def_name(showtext)

            begin_theme_view(PanelView, R_sys_var_theme_PanelView)
                setRectWH(0, _ngux_phonebar_h, _ngux_screen_w, _ngux_content_h)
                begin_theme_view(TextView, R_sys_var_theme_TextView)
                    map(my(showtext))
                    setRectWH(0, 0, _ngux_screen_w, _ngux_content_h)
                    set(TextAlign, ALIGN_CENTER)
                    set(TextValign, VALIGN_MIDDLE)
                    set(Text, "{app_name}")
                end_view
            end_view

            begin_mode({app_client_class_name}_def)
                setMode(APP_MENUBAR_LEFTTEXT, 0, 0)
                setMode(APP_MENUBAR_MIDDLETEXT,STRID_COMMON_ECL_TEXT_SIMPLEX_SOFTKEY_SELECT_MK,{app_name.upper()}_CMD_ENTER)
                setMode(APP_MENUBAR_RIGHTTEXT, STRID_IDLESHORTCUTS_ECL_QTN_NAM_SOFTKEY_BACK, APP_CMD_EXIT)
            end_mode

            begin_controller_modes
                add_mode({app_client_class_name}_def)
            end_controller_modes({app_client_class_name}_def)
        end_ui_res
    end_uis

end_respkg
'''

    source_file_path = {
        root_path.joinpath(f"evb/src/gui/mgapollo/apps/{app_name.lower()}/include/{res_h_file_name}.h"):app_res_h,
        root_path.joinpath(f"evb/src/gui/mgapollo/apps/{app_name.lower()}/include/{app_h_file_name}.h"):app_app_h,
        root_path.joinpath(f"evb/src/gui/mgapollo/apps/{app_name.lower()}/include/{client_h_file_name}.h"):app_client_h,
        root_path.joinpath(f"evb/src/gui/mgapollo/apps/{app_name.lower()}/src/{res_h_file_name}.cpp"):app_res_cpp,
        root_path.joinpath(f"evb/src/gui/mgapollo/apps/{app_name.lower()}/src/{app_h_file_name}.cpp"):app_app_cpp,
        root_path.joinpath(f"evb/src/gui/mgapollo/apps/{app_name.lower()}/src/{client_h_file_name}.cpp"):app_client_cpp,
        root_path.joinpath(f"evb/src/gui/mgapollo/resdesc/{resolution}/{app_name.lower()}/include/{res_c_file_name}.res.c"):app_res_c,
    }

    for file_path, file_content in source_file_path.items():

        folder_path = os.path.dirname(file_path)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        with open(file_path, 'w') as f:
            f.write(file_content)

def create_inner_res():
    pass

def add_entry_function():

    file_name = root_path.joinpath(r'evb/src/gui/mgapollo/apps/src/Apollo.cpp')

    pattern = r'NGBool EntryBootUp (Intent *intent)'

    insert_text = f'''\
#ifdef {app_macro_name}
NGBool Entry{app_name} (Intent *intent)
{{
    AppManager::getInstance()->startApp("{app_name.lower()}", intent);
    return true;
}}
#endif

'''

    insert_text_fun(file_name, pattern, insert_text, 0)

def add_entry_function2():

    file_name = root_path.joinpath(r'evb/src/gui/mgapollo/apps/include/appcommoninclue.h')

    pattern = r'#undef __APP_ENTRIES__'

    insert_text = f'''\
#ifdef {app_macro_name}
NGBool Entry{app_name}(Intent* intent);
#endif

'''

    insert_text_fun(file_name, pattern, insert_text, 0)

    pattern2 = r'#undef __APP_APOLLO__'

    insert_text2 = f'''\
#ifdef {app_macro_name}
#include "{app_h_file_name}.h"
#endif

'''

    insert_text_fun(file_name, pattern2, insert_text2, 0)

def add_mainframe_entry():

    file_name = root_path.joinpath(r'evb/src/gui/mgapollo/apps/launcher/src/MainFrame.cpp')

    pattern_head = r'static APP_ITEM_INFO s_main_app_items[]'
    pattern_end = r'};'

    insert_text = f'''\
#ifdef {app_macro_name}
    {{ Entry{app_name},     STRID_APP_CCA_STR_ID_CCA_SETTING_INFO,
        R_sys_img_app_menu_icon_notepad, R_sys_img_app_menu_icon_small_unuse }},
#endif
'''

    insert_func_end_fun(file_name, pattern_head, pattern_end, insert_text, 0)

def add_app_register():

    file_name = root_path.joinpath(r'evb/src/gui/mgapollo/apps/src/Apollo.cpp')

    pattern_head = 'registerAppFactories'
    pattern_end = r'}'

    insert_text = f'''\
#ifdef {app_macro_name}
    REGISTER_APP("{app_name.lower()}", {app_class_name});
#endif
'''

    insert_func_end_fun(file_name, pattern_head, pattern_end, insert_text, 0)

def arg_parse():
    # Create parameter parser.
    parser = argparse.ArgumentParser(description='This script is used to generate an ASR platform app.')

    # Add positional arguments
    parser.add_argument('app_name', help='Name of the app to be created, for example: NewAPP.')
    parser.add_argument('resolution', help='The resolution of the device, for example: asr-128x160 or asr-128x64-FWP.')

    # Add otions arguments
    parser.add_argument('-v','--version', help='Show version.',action='version',version=f'python version:{sys.version}, soft version: {get_element_value(r"@Version")}')

    # Check if there are no arguments
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)

    # arguments
    args = parser.parse_args()

    # print log
    for key,volue in vars(args).items():
        logging.info(f'{key}:{volue}')

    global app_name
    app_name = args.app_name
    global resolution
    resolution = args.resolution

def start_log():
    # Set the log level to DEBUG to record logs of all levels
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def deal_path():
    global work_path, root_path

    # 文件夹路径。
    if (work_path / 'evb').exists():
        root_path = work_path
        logging.info('Currently in the root directory.')
    elif work_path.name == 'evb':
        root_path = work_path.parent
        logging.info('Currently in the evb directory.')
    else:
        logging.error("The execution path is incorrect! Please place it in the root directory or evb directory.")
        exit(1)

    logging.info(f'work_path:{work_path}')
    logging.info(f'root_path:{root_path}')

if __name__ == "__main__":

    # 启动日志
    start_log()

    # APP 名称，例如：NewApp
    app_name = 'NewApp'

    # 分辨率
    resolution = 'asr-480x960'

    # 处理参数
    arg_parse()

    # 当前工作路径。
    work_path = Path.cwd()

    # 根目录路径
    root_path = work_path

    # 处理路径
    deal_path()

    # APP 文件夹名称，例如：newapp
    app_file_name = f'{app_name.lower()}'

    # APP 配置项的名称，例如：MMI_SUPPORT_NEWAPP
    app_configuration_name = f'MMI_SUPPORT_{app_name.upper()}'

    # APP 宏控的宏名，例如：CONFIG_MMI_SUPPORT_NEWAPP
    app_macro_name = f'CONFIG_MMI_SUPPORT_{app_name.upper()}'

    # APP 类名，例如：NewApp
    app_class_name = app_name

    # 客户端类名，例如：NewAppclient
    app_client_class_name = f'{app_name}Client'

    # 资源文件名称，例如：NewApp_res
    res_h_file_name = f'{app_name}_res'

    # APP 文件名称，例如：NewAppAPP
    app_h_file_name = f'{app_name}APP'

    # 客户端文件名称，例如：NewAppClient
    client_h_file_name = f'{app_name}Client'

    # 资源描述文件名称，例如：newapp
    res_c_file_name = f'{app_name.lower()}'

    # 增加配置项
    add_configuration_items()

    # 添加源文件参与编译。
    modify_cmake_file()

    # 添加头文件引用。
    modify_rules_cmake_file()

    # 添加资源包ID
    add_respkg_id()

    # 添加源文件
    create_source_file()

    # 添加内部资源
    create_inner_res()

    # 添加APP的入口。
    add_entry_function()
    add_entry_function2()

    # 主菜单添加APP 。
    add_mainframe_entry()

    # 注册APP。
    add_app_register()
