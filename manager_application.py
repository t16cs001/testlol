from django.test import TestCase
import datetime

from work_plan.application.manager_application import ManagerApplication
from work_plan.application.employee_application import EmployeeApplication
from work_plan.domain import *
from work_plan.application.DTO.work_plan_dto import WorkPlanDTO, WorkerDTO
from account.models import Account


class ManagerApplicationTests(TestCase):
    manager = ManagerApplication()
    employee = EmployeeApplication()
    
    def test_check_valid_month1(self):
        self.assertRaises(ValueError, self.manager.check_valid_month(1))
        
        # 上のテストと同じ処理やっている
        try:
            self.manager.check_valid_month(5)
        except ValueError:
            self.fail("月が正しくないから ValueError が!!!")
    
    def test_check_valid_month2(self):
        with self.assertRaises(ValueError) as er:
            self.manager.check_valid_month(13)
        raise_except = er.exception
        self.assertEqual(raise_except.args[0], "月が間違った？")
        
    def test_check_valid_day1(self):
        self.assertRaises(ValueError, self.manager.check_valid_day(2018, 12, 21))
        
        # 上のテストと同じ処理やっている
        try:
            self.manager.check_valid_day(2020, 2, 29)
        except ValueError:
            self.fail("日が正しくないから ValueError が!!!")
    
    def test_check_valid_day2(self):
        with self.assertRaises(ValueError) as er:
            self.manager.check_valid_day(2018, 12, 100)
        raise_except = er.exception
        self.assertEqual(raise_except.args[0], "日が間違った？")

    def test_create_month_plan(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [3, 31])
        except :
            self.fail("失敗したよ!!!")
            
    def test_duplicate_create_month_plan(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 1, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 2, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 3, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 4, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 5, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 6, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 7, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 8, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 9, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 10, 2, 2, [3, 31])
            self.manager.create_month_plan(2019, 11, 2, 2, [3, 31])
            self.manager.get_day_plan(2018, 12, 31)
        except :
            self.fail("失敗したよ!!!")

    # DTO
    def test_get_month_plan(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [3, 31])
            month_dto = self.manager.get_month_plan(2018, 12)
            self.assertEqual(month_dto.year, 2018)
            self.assertEqual(month_dto.month, 12)
            day = month_dto.get_day(1)
            self.assertEqual(day.lunch_plan.operating_state, True)
            self.assertEqual(day.lunch_plan.business_hour, '昼')
            day = month_dto.get_day(3)
            self.assertEqual(day.night_plan.operating_state, False)
            day = month_dto.get_day(31)
            self.assertEqual(day.lunch_plan.operating_state, False)
        except :
            self.fail("失敗したよ!!!")
            
    # DTO
    def test_get_day_plan(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [3, 31])
            day_dto = self.manager.get_day_plan(2018, 12, 31)
            self.assertEqual(day_dto.year, 2018)
            self.assertEqual(day_dto.month, 12)
            self.assertEqual(day_dto.day, 31)
            self.assertEqual(day_dto.lunch_plan.operating_state, False)
            self.assertEqual(day_dto.lunch_plan.business_hour, '昼')
            self.assertEqual(day_dto.night_plan.business_hour, '夜')
        except :
            self.fail("失敗したよ!!!")
            
    def test_close_day(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [3, 31])
            day_plan = DayPlan.objects.get_day_plan(2018, 12, 5)
            self.assertEqual(day_plan.operating_state, True)
            self.manager.close_day(2018, 12, 5)
            day_plan = DayPlan.objects.get_day_plan(2018, 12, 5)
            self.assertEqual(day_plan.operating_state, False)
        except :
            self.fail("失敗したよ!!!")
        
    def test_open_day(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [3, 31])
            day_plan = DayPlan.objects.get_day_plan(2018, 12, 31)
            self.assertEqual(day_plan.operating_state, False)
            self.manager.open_day(2018, 12, 31)
            day_plan = DayPlan.objects.get_day_plan(2018, 12, 31)
            self.assertEqual(day_plan.operating_state, True)
        except :
            self.fail("失敗したよ!!!")
            
    def test_update_day_plan(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [3, 31])
            day_plan = DayPlan.objects.get_day_plan(2018, 12, 1)
            self.assertEqual(day_plan.lunch_plan.total_work_time, 4)
            self.assertEqual(day_plan.night_plan.total_work_time, 4)
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            worker = WorkerDTO('001', 'foo')
            worker_list = [worker]
            lunch_plan_dto = WorkPlanDTO(2018, 12, 1, 'lunch', True, datetime.time(11), datetime.time(15), 3, worker_list, 'hello', False)
            night_plan_dto = WorkPlanDTO(2018, 12, 1, 'night', True, datetime.time(18, 30), datetime.time(22), 5, worker_list, 'world', False)
            self.manager.update_day_plan(2018, 12, 1, lunch_plan_dto, night_plan_dto)
            day_plan = DayPlan.objects.get_day_plan(2018, 12, 1)
            self.assertEqual(day_plan.lunch_plan.open_time, datetime.time(11))
            self.assertEqual(day_plan.lunch_plan.required_num, 3)
            self.assertEqual(day_plan.night_plan.required_num, 5)
            self.assertEqual(day_plan.lunch_plan.total_work_time, 4)
            self.assertEqual(day_plan.night_plan.total_work_time, 3.5)
            self.assertEqual(day_plan.lunch_plan.remarks, 'hello')
            self.assertEqual(day_plan.night_plan.remarks, 'world')
        except :
            self.fail("失敗したよ!!!")
            
    def test_close_lunch(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [3, 31])
            lunch_plan = DayPlan.objects.get_day_plan(2018, 12, 1).lunch_plan
            self.assertEqual(lunch_plan.operating_state, True)
            self.manager.close_lunch(2018, 12, 1)
            lunch_plan = DayPlan.objects.get_day_plan(2018, 12, 1).lunch_plan
            self.assertEqual(lunch_plan.operating_state, False)
        except :
            self.fail("失敗したよ!!!")
            
    def test_open_lunch(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [3, 31])
            lunch_plan = DayPlan.objects.get_day_plan(2018, 12, 3).lunch_plan
            self.assertEqual(lunch_plan.operating_state, False)
            self.manager.open_lunch(2018, 12, 3)
            lunch_plan = DayPlan.objects.get_day_plan(2018, 12, 3).lunch_plan
            self.assertEqual(lunch_plan.operating_state, True)
        except :
            self.fail("失敗したよ!!!")
            
    def test_close_night(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [11, 25])
            night_plan = DayPlan.objects.get_day_plan(2018, 12, 12).night_plan
            self.assertEqual(night_plan.operating_state, True)
            self.manager.close_night(2018, 12, 12)
            night_plan = DayPlan.objects.get_day_plan(2018, 12, 12).night_plan
            self.assertEqual(night_plan.operating_state, False)
        except :
            self.fail("失敗したよ!!!")
            
    def test_open_night(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [11, 25])
            night_plan = DayPlan.objects.get_day_plan(2018, 12, 25).night_plan
            self.assertIs(night_plan.operating_state, False)
            self.manager.open_night(2018, 12, 25)
            night_plan = DayPlan.objects.get_day_plan(2018, 12, 25).night_plan
            self.assertIs(night_plan.operating_state, True)
        except :
            self.fail("失敗したよ!!!")
            
    def test_get_all_employees_work_time(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [11, 25])
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            self.employee.add_month_plan(2018, 12, '001', [1, 2], [2, 3])
            work_time_list = self.manager.get_all_employees_work_time(2018, 12)
            work_time = work_time_list.get_employee_work_time('001')
            self.assertEqual(work_time, 16)
            self.manager.add_employee('002', 'foo', 'foo@mail.com')
            self.employee.add_month_plan(2018, 12, '002', [1, 2, 3, 4], [1, 25])
            work_time_list = self.manager.get_all_employees_work_time(2018, 12)
            work_time = work_time_list.get_employee_work_time('002')
            self.assertEqual(work_time, 20)
        except :
            self.fail("失敗したよ!!!")

    # DTO
    def test_get_not_working_employee_lunch(self):
        try:
            self.manager.create_month_plan(2019, 2, 2, 2, [11, 30])
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            self.manager.add_employee('002', 'bar', 'bar@mail.com')
            self.employee.add_month_plan(2019, 2, '001', [1, 2], [2, 3])
            e_dto_list = self.manager.get_not_working_employee_lunch(2019, 2, 1)
            employee = e_dto_list[0]
            self.assertEqual(employee.employee_code, '002')
            self.assertEqual(employee.name, 'bar')
            self.assertEqual(employee.email, 'bar@mail.com')
        except :
            self.fail("失敗したよ!!!")

    # DTO
    def test_get_not_working_employee_night(self):
        try:
            self.manager.create_month_plan(2019, 2, 2, 2, [11, 30])
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            self.manager.add_employee('002', 'bar', 'bar@mail.com')
            self.employee.add_month_plan(2019, 2, '001', [1, 2], [2, 3])
            e_dto_list = self.manager.get_not_working_employee_night(2019, 2, 1)
            first_employee = e_dto_list[0]
            self.assertEqual(first_employee.employee_code, '001')
            self.assertEqual(first_employee.name, 'foo')
            self.assertEqual(first_employee.email, 'foo@mail.com')
            second_employee = e_dto_list[1]
            self.assertEqual(second_employee.employee_code, '002')
            self.assertEqual(second_employee.name, 'bar')
            self.assertEqual(second_employee.email, 'bar@mail.com')
        except :
            self.fail("失敗したよ!!!")

    def test_recruit_lunch(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [11, 25])
            self.manager.add_employee('001', 'foo', 'foo@gmail.com')
            self.manager.add_employee('002', 'bar', 'bar@hotmail.com')
            self.manager.add_employee('003', 'hoge', 'hoge@mail.com')
            self.employee.add_month_plan(2018, 12, '001', [1, 2], [2, 3, 4])
            self.employee.add_month_plan(2018, 12, '002', [1, 2], [2, 3])
            self.employee.add_month_plan(2018, 12, '003', [2], [3])
            
            lunch_plan = DayPlan.objects.get_day_plan(2018, 12, 1).lunch_plan
            self.assertEqual(lunch_plan.recruitment_status, False)
            self.manager.recruit_lunch(2018, 12, 1, 'localhost:3000')
            lunch_plan = DayPlan.objects.get_day_plan(2018, 12, 1).lunch_plan
            self.assertEqual(lunch_plan.recruitment_status, True)
        except :
            self.fail("失敗したよ!!!")
        
    def test_recruit_night(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [11, 25])
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            self.employee.add_month_plan(2018, 12, '001', [1, 2], [2, 3, 4])
            
            night_plan = DayPlan.objects.get_day_plan(2018, 12, 1).night_plan
            self.assertEqual(night_plan.recruitment_status, False)
            self.manager.recruit_night(2018, 12, 1, 'localhost:8080')
            night_plan = DayPlan.objects.get_day_plan(2018, 12, 1).night_plan
            self.assertEqual(night_plan.recruitment_status, True)
        except :
            self.fail("失敗したよ!!!")

    # DTO
    def test_get_recent_recruitment(self):
        try:
            self.manager.create_month_plan(2018, 12, 2, 2, [11, 25])
            self.manager.recruit_lunch(2018, 12, 1, 'localhost:3000')
            self.manager.recruit_night(2018, 12, 1, 'localhost:8080')
            recruitment_list = self.manager.get_recent_recruitment()
            self.assertEqual(len(recruitment_list), 2)
            self.manager.recruit_lunch(2018, 12, 5, 'localhost:3000')
            self.manager.recruit_lunch(2018, 12, 10, 'localhost:3000')
            self.manager.recruit_lunch(2018, 12, 11, 'localhost:3000') # 休業日なので、募集が通らないはず
            self.manager.recruit_night(2018, 12, 16, 'localhost:8080')
            recruitment_list = self.manager.get_recent_recruitment()
            self.assertEqual(len(recruitment_list), 5)
            for each in recruitment_list:
                self.assertEqual(each.recruitment_status, True)
        except :
            self.fail("失敗したよ!!!")
        
    def test_add_employee(self):
        try:
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            employee = Employee.objects.get_employee('001')
            self.assertEqual(employee.code, '001')
            self.assertEqual(employee.name, 'foo')
            self.assertEqual(employee.email, 'foo@mail.com')
            account = Account.objects.get(employee_code='001')
            self.assertIs(account.is_employee, True)
        except :
            self.fail("失敗したよ!!!")
            
    # DTO
    def test_get_employee(self):
        try:
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            e_dto = self.manager.get_employee('001')
            self.assertEqual(e_dto.employee_code, '001')
            self.assertEqual(e_dto.name, 'foo')
            self.assertEqual(e_dto.email, 'foo@mail.com')
        except :
            self.fail("失敗したよ!!!")
    
    # DTO
    def test_get_all_employees(self):
        try:
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            self.manager.add_employee('002', 'bar', 'bar@mail.com')
            e_dto_list = self.manager.get_all_employees()
            first_employee = e_dto_list[0]
            self.assertEqual(first_employee.employee_code, '001')
            self.assertEqual(first_employee.name, 'foo')
            self.assertEqual(first_employee.email, 'foo@mail.com')
            second_employee = e_dto_list[1]
            self.assertEqual(second_employee.employee_code, '002')
            self.assertEqual(second_employee.name, 'bar')
            self.assertEqual(second_employee.email, 'bar@mail.com')
        except :
            self.fail("失敗したよ!!!")
    
    def test_delete_employee(self):
        try:
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            employee = Employee.objects.get_employee('001')
            self.assertEqual(employee.code, '001')
            self.manager.delete_employee('001')
            employee = Employee.objects.get_employee('001')
            self.assertEqual(employee, None)
        except :
            self.fail("失敗したよ!!!")
            
    def test_change_employee_settings(self):
        try:
            self.manager.add_employee('001', 'foo', 'foo@mail.com')
            employee = Employee.objects.get_employee('001')
            self.assertEqual(employee.name, 'foo')
            self.assertEqual(employee.email, 'foo@mail.com')
            self.manager.change_employee_settings('001', 'test', 'test@mail.com')
            employee = Employee.objects.get_employee('001')
            self.assertEqual(employee.name, 'test')
            self.assertEqual(employee.email, 'test@mail.com')
        except :
            self.fail("失敗したよ!!!")
        
        