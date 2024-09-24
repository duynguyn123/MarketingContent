from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug

class BlogMarketingContent(models.Model):
    _name = 'marketing.blog'
    _description = 'Blog Marketing Content'
    _inherits = {'marketing.content': 'content_id'}

    content_id = fields.Many2one('marketing.content', string='Marketing Content', required=True, ondelete='cascade', auto_join=True)
    blog_id = fields.Many2one('blog.post', string='Blog')
    temp_image = fields.Binary(string='Temporary Image', attachment=False)
    content = fields.Text(string='Subtitle')  # Ensure this field is used for the subtitle
    url = fields.Char(string='URL')

    @api.model
    def create(self, vals):
        # Create a marketing.content record
        content_vals = {
            'content': vals.get('content', ''),
            'url': vals.get('url', ''),
            'include_link': vals.get('include_link', False)
        }
        content = self.env['marketing.content'].create(content_vals)
        vals['content_id'] = content.id

        res = super(BlogMarketingContent, self).create(vals)

        # If temp_image is provided, create an image record
        if res.temp_image:
            image = self.env['marketing.content.image'].create({
                'content_id': res.content_id.id,
                'image': res.temp_image,
                'datas': res.temp_image,
            })
            res.content_id.write({'image_ids': [(4, image.id)]})
            res.temp_image = False

        return res

    def write(self, vals):
        # Update marketing.content record
        content_vals = {}
        if 'content' in vals:
            content_vals['content'] = vals['content']
        if 'url' in vals:
            content_vals['url'] = vals['url']
        if 'include_link' in vals:
            content_vals['include_link'] = vals['include_link']

        if content_vals:
            self.content_id.write(content_vals)

        res = super(BlogMarketingContent, self).write(vals)

        # If temp_image is provided, create an image record
        if 'temp_image' in vals and vals.get('temp_image'):
            image = self.env['marketing.content.image'].create({
                'content_id': self.content_id.id,
                'image': vals.get('temp_image'),
                'datas': vals.get('temp_image'),
            })
            self.content_id.write({'image_ids': [(4, image.id)]})
            self.temp_image = False

        return res

    @api.onchange('blog_id')
    def _onchange_blog_post(self):
        if self.blog_id:
            self.content = self.blog_id.subtitle or ''
            self.url = '/blog/%s/post/%s' % (slug(self.blog_id.blog_id), slug(self.blog_id))

            # Check for the correct image field in blog.post
            if hasattr(self.blog_id, 'image'):
                self.temp_image = self.blog_id.image
            else:
                self.temp_image = False
        else:
            self.content = ''
            self.url = ''
            self.temp_image = False
