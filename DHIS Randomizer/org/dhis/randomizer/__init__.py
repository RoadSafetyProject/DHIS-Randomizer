# from openpyxl import load_workbook
# 
# wb = load_workbook('E:/randomizer/PersonsMaleAndFemaleNames.xlsx') 
# ws = wb.active
# 
# data = []
# col_name = 'A'
# start_row = 2
# end_row = 99
# 
# range_expr = "{col}{start_row}:{col}{end_row}".format(
#     col=col_name, start_row=start_row, end_row=len(ws.rows))
# 
# for (time_cell,) in ws.iter_rows(range_string=range_expr):
#     if(time_cell.value == None):
#         break
#     data.append(time_cell.value)
#     
# col_name = 'B'
# start_row = 2
# end_row = 99
# 
# range_expr = "{col}{start_row}:{col}{end_row}".format(
#     col=col_name, start_row=start_row, end_row=len(ws.rows))
# 
# for (time_cell,) in ws.iter_rows(range_string=range_expr):
#     if(time_cell.value == None):
#         break
#     data.append(time_cell.value)
# 
# import json
# with open('E:/randomizer/names.json', 'w') as outfile:
#     json.dump(data, outfile)
import Settings
import Program
import json
import HttpRequestor


settingHandler = Settings.SettingHandler('E:/randomizer/')
dhishttpReq = HttpRequestor.HttpRequestor(settingHandler.getDHISUrl(),
                                          settingHandler.getDHISUserName(),
                                          settingHandler.getDHISUserPassword());
                            

# while True:
#     resp, content = dhishttpReq.get("events.json")
#     eventsFromServer = json.loads(content)
#     print json.dumps(eventsFromServer)
#     for event in eventsFromServer["events"]:
#         resp, content = dhishttpReq.delete("events/" +event["event"])


programHandler = Program.ProgramHandler(settingHandler)
while (len(programHandler.getProgramDependencies()) != 0):
    programDep = programHandler.getNextProgram()
    program = programHandler.getProgram(programDep["name"])
    program.randomizeData()