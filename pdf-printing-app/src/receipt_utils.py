def generate_receipt(job_data):
    receipt_lines = []
    receipt_lines.append(f"Job ID: {job_data.get('JobID', 'N/A')}")
    receipt_lines.append(f"Quantity: {job_data.get('quantity', 'N/A')}")
    receipt_lines.append(f"Paper Size: {job_data.get('size', 'N/A')}")
    receipt_lines.append(f"Date Wanted: {job_data.get('date', 'N/A')}")
    receipt_lines.append(f"Staple: {job_data.get('staple', 'N/A')}")
    receipt_lines.append(f"Double Sided: {job_data.get('2side', 'N/A')}")
    receipt_lines.append(f"Hole Punch: {job_data.get('hole', 'N/A')}")
    receipt_lines.append(f"Requested By: {job_data.get('who', 'N/A')}")
    receipt_lines.append(f"Location: {job_data.get('where', 'N/A')}")

    return "\n".join(receipt_lines)