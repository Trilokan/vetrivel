# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta

PROGRESS_INFO = [('draft', 'Draft'),
                 ('confirmed', 'Waiting For Approval'),
                 ('cancelled', 'Cancelled'),
                 ('approved', 'Approved')]
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
CURRENT_TIME_INDIA = datetime.now().strftime("%d-%m-%Y %H:%M:%S")


class OnDutyApplication(models.Model):
    _name = "on.duty.application"

    person_id = fields.Many2one(comodel_name="arc.person", string="Person", required=True)
    reason = fields.Text(string="Reason")
    total_hours = fields.Float(string="Total Hours", compute="update_total_hours")
    line_ids = fields.One2many(comodel_name="on.duty.line", inverse_name="on_duty_id")
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Text(string="Writter", track_visibility="always")

    def update_total_hours(self):
        for rec in self:
            items = self.line_ids

            total_hours = 0
            for item in items:
                total_hours = total_hours + item.total_hours

            rec.total_hours = total_hours

    @api.multi
    def trigger_confirm(self):
        recs = self.line_ids
        for rec in recs:
            rec.check_month()

        writter = "On-Duty application confirmed by {0} on {1}".format(self.env.user.name, CURRENT_TIME_INDIA)
        data = {"progress": "confirmed", "writter": writter}

        self.write(data)

    @api.multi
    def trigger_cancel(self):
        recs = self.line_ids
        for rec in recs:
            rec.check_month()

        writter = "On-Duty application cancelled by {0} on {1}".format(self.env.user.name, CURRENT_TIME_INDIA)
        data = {"progress": "cancelled", "writter": writter}

        self.write(data)

    @api.multi
    def trigger_approve(self):
        recs = self.line_ids
        for rec in recs:
            rec.update_work_sheet()

        writter = "On-Duty application approved by {0} on {1}".format(self.env.user.name, CURRENT_TIME_INDIA)
        data = {"progress": "approved", "writter": writter}

        self.write(data)

    @api.model
    def create(self, vals):
        vals["writter"] = "On-Duty application created by {0}".format(self.env.user.name)
        return super(OnDutyApplication, self).create(vals)


class OnDutyLine(models.Model):
    _name = "on.duty.line"

    date = fields.Date(string="Date", required=True)
    total_hours = fields.Float(string="Total Hours", default=0.0, required=True)
    on_duty_id = fields.Many2one(comodel_name="on.duty.application", string="On Duty")

    def check_month(self):
        attendance_id = self.env["employee.attendance"].search([("attendance_id.date", "=", self.date),
                                                                ("person_id", "=", self.on_duty_id.person_id.id)])

        if not attendance_id:
            raise exceptions.ValidationError("Error! Month is not configured")

        if attendance_id.attendance_id.month_id.progress == "closed":
            raise exceptions.ValidationError("Error! Month is already closed")

    def update_work_sheet(self):
        self.check_month()
        attendance_id = self.env["employee.attendance"].search([("attendance_id.date", "=", self.date),
                                                                ("person_id", "=", self.on_duty_id.person_id.id)])
        attendance_id.on_duty_hours = self.total_hours

