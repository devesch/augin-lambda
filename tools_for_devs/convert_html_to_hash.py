import hashlib
import base64

# Your script
script = "<script type=\"text/javascript\">var Tawk_API=Tawk_API||{},Tawk_LoadStart=new Date;window.Tawk_API.visitor={name:\"{{tawk_user_name_val}}\",email:\"{{tawk_user_email_val}}\"},function(){var a=document.createElement(\"script\"),e=document.getElementsByTagName(\"script\")[0];a.async=!0,a.src=\"https://embed.tawk.to/{{tawk_api_val}}\",a.charset=\"UTF-8\",a.setAttribute(\"crossorigin\",\"*\"),e.parentNode.insertBefore(a,e)}();</script>"

# Calculate SHA-256 hash
hash = hashlib.sha256(script.encode('utf-8')).digest()

# Encode in Base64
base64_hash = base64.b64encode(hash).decode('utf-8')

print(f"The CSP hash for your script is: sha256-{base64_hash}")