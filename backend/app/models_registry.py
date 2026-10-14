"""
Central models registry.

Imports every ORM model module so that `Base.metadata` (app.database.Base)
is fully populated with all tables before Alembic (or any code needing
the complete schema) inspects it. Each model is defined within its
owning business module (per TRD v1.0 Section 8's module-boundary
design) — this file exists purely to give Alembic's `env.py` a single,
reliable import target, not to hold any schema or logic itself.

Add a new `from app.modules.<name> import models as _<name>_models` line
here whenever a new module's models.py is introduced in a later phase.
"""

from app.modules.forecasting import models as _forecasting_models  # noqa: F401
from app.modules.historical_data import models as _historical_data_models  # noqa: F401
from app.modules.locations import models as _locations_models  # noqa: F401
from app.modules.meal_types import models as _meal_types_models  # noqa: F401
from app.modules.planned_quantities import models as _planned_quantities_models  # noqa: F401
from app.modules.recommendations import models as _recommendations_models  # noqa: F401
from app.modules.users import models as _users_models  # noqa: F401

from app.database import Base  # noqa: E402,F401 - re-exported for convenience
