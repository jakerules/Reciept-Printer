def generate_receipt(job_data):
    receipt_lines = []
    receipt_lines.append(f"Job ID: {job_data.get('job_id', 'N/A')}")
    receipt_lines.append(f"Quantity: {job_data.get('quantity', 'N/A')}")
    receipt_lines.append(f"Paper Size: {job_data.get('paper_size', 'N/A')}")
    receipt_lines.append(f"Date Wanted: {job_data.get('date_wanted', 'N/A')}")
    receipt_lines.append(f"Pages: {job_data.get('pages', 'N/A')}")
    receipt_lines.append(f"Staple: {job_data.get('staple', 'N/A')}")
    receipt_lines.append(f"Double Sided: {job_data.get('double_sided', 'N/A')}")
    receipt_lines.append(f"Hole Punch: {job_data.get('hole_punch', 'N/A')}")

    return "\n".join(receipt_lines)