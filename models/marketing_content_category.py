from odoo import models, fields, api
import logging
import random

_logger = logging.getLogger(__name__)

class ContentCategory(models.Model):
    _name = 'content.category'
    _description = 'Content Categories List'
    
    
    name = fields.Char(string='Category Name', required=True)
    content_category_id = fields.Char(string='Category ID', readonly=True)
    description = fields.Text(string='Description')
    parent_category = fields.Many2one('content.category', string='Parent Category', index=True, ondelete='set null')
    parent_category_name = fields.Char(string='Parent Category Name', compute='_compute_parent_category_name', store=True)
    parent_category_path = fields.Char(string='Parent Path')
    blog_category = fields.Many2many('blog.tag', string='Blog Categories')
    product_category = fields.Many2many('product.category', string='Product Categories')
    subcategory_ids = fields.One2many('content.category', 'parent_category', string='Subcategories')
    content_ids = fields.Many2many('marketing.content', 'content_category_rel', 'category_id', 'content_id', string='Marketing Content')

    # Compute parent category name
    @api.depends('parent_category')
    def _compute_parent_category_name(self):
        for record in self:
            record.parent_category_name = record.parent_category.name if record.parent_category else False

    @api.model
    def _generate_category_id(self):
        # Generate a random number with 8 digits and format it
        random_number = random.randint(0, 99999999)
        return 'CaID{0:08d}'.format(random_number)

    @api.model
    def create(self, vals):
        # Set content_category_id if not provided
        if not vals.get('content_category_id'):
            vals['content_category_id'] = self._generate_category_id()
        return super(ContentCategory, self).create(vals)

    def _create_or_update_category(self, categories, parent_category_id, parent_category_path):
        for category in categories:
            name = category.get('name')
            path = f"{parent_category_path}/{name}" if parent_category_path else name

            category_record = self.search([
                ('name', '=', name),
                ('parent_category', '=', parent_category_id)
            ], limit=1)
            if category_record:
                category_record.write({
                    'description': category.get('description', ''),
                    'parent_category': parent_category_id,
                    'parent_category_path': path,
                })
            else:
                self.create({
                    'name': name,
                    'content_category_id': self._generate_category_id(),
                    'description': category.get('description', ''),
                    'parent_category': parent_category_id,
                    'parent_category_path': path,
                })

            subcategories = category.get('content_page_categories', [])
            if subcategories:
                self._create_or_update_category(subcategories, category_record.id, path)

    @api.model
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.content_category_id})" if record.content_category_id else record.name
            result.append((record.id, name))
        return result

    # Action to add existing marketing content
    @api.model
    def create(self, vals):
        if not vals.get('content_category_id'):
            vals['content_category_id'] = self._generate_category_id()
        return super(ContentCategory, self).create(vals)

    def action_add_existing_content(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Existing Marketing Content',
            'view_mode': 'form',
            'res_model': 'marketing.content',
            'target': 'new',
            'context': {'default_category_id': self.id},
            'domain': [('id', 'not in', self.content_ids.ids)] 
        }
