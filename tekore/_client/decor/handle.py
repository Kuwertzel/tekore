from requests import Request, Response, HTTPError

from tekore._error import errors
from tekore.model import PlayerErrorReason

error_format = """Error in {url}:
{code}: {msg}
"""


def parse_json(response):
    """Get JSON dict if available."""
    try:
        return response.json()
    except ValueError:
        return None


def parse_error_reason(response):
    """Extract error reason from response content."""
    content = parse_json(response)
    reason = getattr(response, 'reason', '')

    if content is None:
        return reason

    error = content['error']
    message = error.get('message', reason)
    if 'reason' in error:
        message += '\n' + PlayerErrorReason[error['reason']].value
    return message


def handle_errors(request: Request, response: Response) -> None:
    """Examine response and raise errors accordingly."""
    if response.status_code >= 400:
        error_str = error_format.format(
            url=response.url,
            code=response.status_code,
            msg=parse_error_reason(response)
        )
        error_cls = errors.get(response.status_code, HTTPError)
        raise error_cls(error_str, request=request, response=response)
