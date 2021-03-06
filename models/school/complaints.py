# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta

PROGRESS_INFO = [('draft', 'Draft'), ('registered', 'Registered')]
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
CURRENT_TIME_INDIA = datetime.now().strftime("%d-%m-%Y %H:%M:%S")


class StudentComplaints(models.Model):
    _name = "student.complaint"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", readonly=True)
    date = fields.Date(string="Date", default=CURRENT_DATE, required=True)
    student_id = fields.Many2one(comodel_name="arc.student", string="Student", required=True)
    details = fields.Text(string="Complaint Details", required=True)
    attachment_ids = fields.Many2many(comodel_name="ir.attachment", string="Attachment")
    complaints_by = fields.Many2one(comodel_name="arc.person", string="Complaints By", required=True)
    progress = fields.Selection(selection=PROGRESS_INFO, string="Progress", default="draft")
    writter = fields.Char(string="Writter", track_visibility="always")

    @api.multi
    def trigger_register(self):
        writter = "Complaints register by {0} on {1}".format(self.env.user.name, CURRENT_TIME_INDIA)
        self.write({"progress": "registered", "writter": writter})

    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code(self._name)
        return super(StudentComplaints, self).create(vals)
