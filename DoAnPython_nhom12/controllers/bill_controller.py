from services.bill_service import BillService

class BillController:
    def __init__(self, role="Lễ tân"):
        self.role = role
        self.service = BillService()

    def get_bills(self):
        return self.service.load_bills()

    def calculate_summary_report(self, bills_data):
        total_revenue = 0
        total_bills = len(bills_data)
        total_items_count = 0
        
        pay_methods_revenue = {}
        pay_methods_count = {}
        dish_stats = {}

        for b in bills_data:
            total_revenue += b.get("total_amount", 0)
            
            method = b.get("payment_method", "Chưa rõ")
            pay_methods_revenue[method] = pay_methods_revenue.get(method, 0) + b.get("total_amount", 0)
            pay_methods_count[method] = pay_methods_count.get(method, 0) + 1
            
            items = b.get("items", [])
            for item in items:
                qty = item.get("qty", 1)
                name = item.get("name", "Món khác")
                total_items_count += qty
                dish_stats[name] = dish_stats.get(name, 0) + qty

        sorted_dishes = sorted(dish_stats.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_revenue": total_revenue,
            "total_bills": total_bills,
            "total_items_count": total_items_count,
            "pay_methods_revenue": pay_methods_revenue,
            "pay_methods_count": pay_methods_count,
            "sorted_dishes": sorted_dishes
        }

    def get_bill_detail(self, bills_data, bill_id):
        return next((b for b in bills_data if b.get("id") == bill_id), None)