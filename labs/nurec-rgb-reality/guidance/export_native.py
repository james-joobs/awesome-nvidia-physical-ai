"""Load the independent loss registration before native model export."""
import json, os, sys
sys.path.insert(0,'/lab/guidance')
from normal_loss import rgb_normal_cosine
from nre.utils.io.export.gaussian_plys import export_gaussian_plys

export_gaussian_plys.main(args=json.loads(os.environ['RGB_EXPORT_ARGS']),standalone_mode=False)
