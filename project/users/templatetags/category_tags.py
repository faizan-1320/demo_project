# templatetags/category_tags.py

from django import template
from django.utils.safestring import mark_safe
from project.product.models import Category

register = template.Library()

def render_category_tree(categories, parent_id=None, selected_category_id=None):
    html = ''
    
    # Filter categories to get only active and not deleted ones
    for category in categories.filter(parent_id=parent_id, is_active=True, is_delete=False):
        # Check if the category has active and not deleted subcategories
        has_subcategories = category.subcategories.filter(is_active=True, is_delete=False).exists()
        is_active_category = selected_category_id == category.id

        # Panel for category
        html += '<div class="panel panel-default">'
        html += '    <div class="panel-heading">'
        html += '        <h4 class="panel-title">'

        if has_subcategories:
            # Link for category name to navigate to related products
            html += f'            <a href="?category={category.id}">'
            html += f'                {category.category_name}'
            html += '            </a>'
            
            # Separate anchor for collapse functionality
            html += f'            <a data-toggle="collapse" '
            html += f'               href="#collapse-{category.id}" '
            html += f'               class="collapse-icon">'
            html += f'                <span class="badge pull-right"><i class="fa fa-plus"></i></span>'
            html += '            </a>'
        else:
            # Anchor link for category without subcategories
            html += f'            <a href="?category={category.id}">'
            html += f'                {category.category_name}'
            html += '            </a>'

        html += '        </h4>'
        html += '    </div>'

        if has_subcategories:
            # Collapse panel for subcategories
            html += f'    <div id="collapse-{category.id}" class="panel-collapse collapse {"in" if is_active_category else ""}">'
            html += '        <div class="panel-body">'
            html += render_category_tree(categories, parent_id=category.id, selected_category_id=selected_category_id)
            html += '        </div>'
            html += '    </div>'

        html += '</div>'

    return mark_safe(html)

@register.simple_tag(takes_context=True)
def render_category_tree_tag(context):
    categories = Category.objects.filter(is_active=True, is_delete=False)
    selected_category_id = context.get('selected_category_id', None)
    return render_category_tree(categories, selected_category_id=selected_category_id)

@register.filter
def is_out_of_stock(quantity):
    return quantity == 0

@register.filter
def get_category_name(category_id):
    try:
        category = Category.objects.get(id=category_id)
        return category.category_name
    except Category.DoesNotExist:
        return "Unknown Category"